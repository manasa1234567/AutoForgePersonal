from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from ..models.schemas import AuditEvent, SkillRecipe, SkillStatus
from ..repositories.skill_repository import InMemorySkillRepository, SkillRepository


class SkillRegistry:
    """Loads the markdown seed pack, governs lifecycle, and retrieves approved recipes."""

    def __init__(self, repository: SkillRepository | None = None) -> None:
        self._repository = repository or InMemorySkillRepository(self._load_seed_pack())

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
        return [recipe for recipe in ranked if score(recipe)[0] > 0][:max(0, min(limit, 5))]

    def get(self, recipe_id: str) -> SkillRecipe:
        return self._repository.get(recipe_id)

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
