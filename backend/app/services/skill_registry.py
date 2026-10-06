from __future__ import annotations

import hashlib
import re
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..models.schemas import AuditEvent, SkillRecipe, SkillStatus
from ..repositories.skill_repository import InMemorySkillRepository, SkillRepository

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Loads the markdown seed pack, governs lifecycle, and retrieves approved recipes."""

    def __init__(self, repository: SkillRepository | None = None) -> None:
        if repository is not None:
            self._repository = repository
        elif os.getenv("AUTOFORGE_PERSISTENCE", "local").strip().lower() == "azure":
            from ..repositories.azure_repositories import AzureSkillRepository

            self._repository = AzureSkillRepository()
            for recipe in self._load_seed_pack():
                try:
                    self._repository.get(recipe.id)
                except KeyError:
                    self._repository.save(recipe)
            self._repository.backfill()
        else:
            self._repository = InMemorySkillRepository(self._load_seed_pack())

    @staticmethod
    def _load_seed_pack() -> list[SkillRecipe]:
        path = Path(__file__).resolve().parents[1] / "skills" / "seed_recipes.md"
        content = path.read_text(encoding="utf-8")
        agent = ""
        recipes: list[SkillRecipe] = []
        lines = content.splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            if line.startswith("## ") and not line.startswith("### "):
                agent_heading = re.match(r"^## \d+\.\s*(.+)$", line)
                if agent_heading:
                    agent = agent_heading.group(1).strip()
            heading = re.match(r"^### (SKL-[A-Z]+-\d+):\s*(.+)$", line)
            if not heading:
                index += 1
                continue
            recipe_id, title = heading.group(1), heading.group(2).strip()
            index += 1
            body_lines: list[str] = []
            while index < len(lines) and not lines[index].startswith("### ") and not (
                lines[index].startswith("## ") and not lines[index].startswith("### ")
            ):
                body_lines.append(lines[index])
                index += 1
            fields: dict[str, str] = {}
            active_field = ""
            collected: dict[str, list[str]] = {}
            for raw_line in body_lines:
                line = raw_line.strip()
                field_match = re.match(r"^- \*\*(Tags|Use when|Inputs|Steps|Done when|Pitfalls|Output)\*\*:\s*(.*)$", line)
                if field_match:
                    active_field = field_match.group(1)
                    fields[active_field] = field_match.group(2).strip()
                    collected.setdefault(active_field, [])
                    if active_field in {"Steps", "Inputs", "Pitfalls"} and fields[active_field]:
                        collected[active_field].append(fields[active_field])
                    continue
                if not active_field:
                    continue
                if re.match(r"^\d+\.\s+", line):
                    collected.setdefault(active_field, []).append(re.sub(r"^\d+\.\s+", "", line))
                elif line.startswith("- ") and active_field in {"Inputs", "Pitfalls", "Steps"}:
                    collected.setdefault(active_field, []).append(line[2:].strip())
                elif line.startswith("-"):
                    active_field = ""

            tags = [tag.strip() for tag in fields.get("Tags", "").split(",") if tag.strip()]
            recipe = SkillRecipe(
                id=recipe_id,
                agent=agent,
                title=title,
                tags=tags,
                use_when=fields.get("Use when", ""),
                inputs=collected.get("Inputs", []),
                steps=collected.get("Steps", []),
                done_when=fields.get("Done when", ""),
                pitfalls=collected.get("Pitfalls", []),
                output=fields.get("Output", ""),
                version="0.1",
                status="draft",
            )
            recipe.audit.append(AuditEvent(
                time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                stage="Seed",
                message="Imported from AutoForge Agent Recipes seed pack; awaiting human review.",
                agent="Skill Registry",
            ))
            recipes.append(recipe)
        recipe_ids = [recipe.id for recipe in recipes]
        if len(recipe_ids) != len(set(recipe_ids)):
            raise RuntimeError("Seed skill pack contains duplicate recipe IDs")
        invalid = [recipe.id for recipe in recipes if not recipe.agent or not recipe.tags or not recipe.steps]
        if invalid:
            raise RuntimeError(f"Seed skill pack is missing required recipe fields: {', '.join(invalid)}")
        if not recipes:
            raise RuntimeError("Seed skill pack contains no recipes")
        return recipes

    def list(self, *, status: SkillStatus | None = None, agent: str | None = None, query: str = "") -> list[SkillRecipe]:
        items = self._repository.list()
        if status:
            items = [item for item in items if item.status == status]
        if agent:
            items = [item for item in items if item.agent.lower() == agent.lower()]
        needle = query.strip().lower()
        if needle:
            items = [item for item in items if needle in self._searchable(item)]
        return items

    def retrieve(self, *, agent: str, query: str, limit: int = 5) -> list[SkillRecipe]:
        bounded_limit = max(0, min(limit, 5))
        search = getattr(self._repository, "search_approved", None)
        if callable(search) and bounded_limit:
            try:
                matches = search(agent=agent, query=query, limit=bounded_limit)
                if matches:
                    return matches
            except Exception:
                logger.warning(
                    "Azure skill search failed; using approved-only lexical retrieval",
                    exc_info=True,
                )
        candidates = self.list(status="approved", agent=agent)
        query_terms = set(re.findall(r"[a-z0-9_-]{2,}", query.lower()))

        def score(recipe: SkillRecipe) -> tuple[int, str]:
            fields = {
                "title": set(re.findall(r"[a-z0-9_-]{2,}", recipe.title.lower())),
                "tags": set(tag.lower() for tag in recipe.tags),
                "body": set(re.findall(r"[a-z0-9_-]{2,}", self._searchable(recipe))),
            }
            return (len(query_terms & fields["title"]) * 5 + len(query_terms & fields["tags"]) * 4 + len(query_terms & fields["body"]), recipe.id)
        ranked = sorted(candidates, key=score, reverse=True)
        return [recipe for recipe in ranked if score(recipe)[0] > 0][:bounded_limit]

    def get(self, recipe_id: str) -> SkillRecipe:
        return self._repository.get(recipe_id)

    @staticmethod
    def prepare_repair_candidate(candidate: object) -> SkillRecipe | None:
        """Validate an untrusted Coder suggestion without persisting or approving it."""
        if not isinstance(candidate, dict):
            return None

        def text(camel: str, snake: str, maximum: int) -> str | None:
            value = candidate.get(camel, candidate.get(snake))
            if not isinstance(value, str):
                return None
            value = value.strip()
            return value[:maximum] if value else None

        def strings(key: str, maximum_items: int, maximum_length: int) -> list[str] | None:
            value = candidate.get(key)
            if not isinstance(value, list) or not value or len(value) > maximum_items:
                return None
            if not all(isinstance(item, str) and item.strip() for item in value):
                return None
            return [item.strip()[:maximum_length] for item in value]

        title = text("title", "title", 120)
        use_when = text("useWhen", "use_when", 500)
        done_when = text("doneWhen", "done_when", 500)
        output = text("output", "output", 500)
        tags = strings("tags", 12, 50)
        inputs = strings("inputs", 12, 200)
        steps = strings("steps", 12, 500)
        pitfalls = candidate.get("pitfalls", [])
        if not isinstance(pitfalls, list) or len(pitfalls) > 12 or not all(
            isinstance(item, str) for item in pitfalls
        ):
            return None
        pitfalls = [item.strip()[:500] for item in pitfalls if item.strip()]
        if not all((title, use_when, done_when, output, tags, inputs, steps)):
            return None

        searchable = " ".join([title, use_when, done_when, output, *tags, *inputs, *steps, *pitfalls])
        if re.search(
            r"(?i)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*\S+|"
            r"-----BEGIN [^-]*PRIVATE KEY-----|https?://[^\s/@]+:[^\s/@]+@",
            searchable,
        ):
            return None
        if re.search(r"(?i)ignore (?:all )?previous instructions|disable (?:authentication|security)|bypass (?:security|tests)", searchable):
            return None

        canonical = json.dumps(
            {"title": title, "useWhen": use_when, "steps": steps, "doneWhen": done_when},
            sort_keys=True,
            separators=(",", ":"),
        )
        recipe_id = "SKL-GEN-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12].upper()
        return SkillRecipe(
            id=recipe_id,
            agent="Coder Agent",
            title=title,
            tags=tags,
            use_when=use_when,
            inputs=inputs,
            steps=steps,
            done_when=done_when,
            pitfalls=pitfalls,
            output=output,
            version="1.0.0",
            status="draft",
        )

    def save_repair_candidate(self, recipe: SkillRecipe, *, build_id: str) -> SkillRecipe:
        try:
            existing = self.get(recipe.id)
        except KeyError:
            existing = None
        if existing is not None:
            return existing
        recipe = recipe.model_copy(update={
            "status": "draft",
            "audit": recipe.audit + [AuditEvent(
                time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                stage="Evolver",
                message="Candidate derived from a repaired deployment that passed its smoke test; human review required.",
                agent="Skill Evolver",
                metadata={"buildId": build_id, "evidence": "successful-deployment-repair"},
            )],
        })
        self._repository.save(recipe)
        return recipe

    def decide(self, recipe_id: str, *, decision: str, reason: str = "") -> SkillRecipe:
        recipe = self.get(recipe_id)
        transitions: dict[str, SkillStatus] = {
            "submit": "pending_approval",
            "approve": "approved",
            "reject": "rejected",
            "deprecate": "deprecated",
        }
        if decision not in transitions:
            raise ValueError("Unsupported skill lifecycle decision")
        if recipe.status not in {"draft", "pending_approval", "approved"}:
            raise ValueError(f"Cannot {decision} a recipe in '{recipe.status}' status")
        if decision == "submit" and recipe.status != "draft":
            raise ValueError("Only a draft recipe can be submitted for review")
        if decision in {"approve", "reject"} and recipe.status != "pending_approval":
            raise ValueError("Only a recipe pending human review can be approved or rejected")
        if decision == "deprecate" and recipe.status != "approved":
            raise ValueError("Only an approved recipe can be deprecated")
        recipe.status = transitions[decision]
        recipe.audit.append(AuditEvent(
            time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            stage="Governance",
            message=f"Human reviewer selected {decision}." + (f" Reason: {reason.strip()}" if reason.strip() else ""),
            agent="Local reviewer (authentication not configured)",
            severity="warning" if decision in {"reject", "deprecate"} else "info",
        ))
        self._repository.save(recipe)
        return recipe

    @staticmethod
    def _searchable(recipe: SkillRecipe) -> str:
        return " ".join([
            recipe.id, recipe.agent, recipe.title, " ".join(recipe.tags), recipe.use_when,
            " ".join(recipe.inputs), " ".join(recipe.steps), recipe.done_when,
            " ".join(recipe.pitfalls), recipe.output,
        ]).lower()


skill_registry = SkillRegistry()
