from __future__ import annotations

from app.models.schemas import SkillRecipe
from app.repositories.azure_repositories import AzureSkillRepository
from app.repositories.skill_repository import InMemorySkillRepository
from app.services.skill_registry import SkillRegistry


def recipe(*, recipe_id: str, agent: str = "Coder Agent", status: str = "approved") -> SkillRecipe:
    return SkillRecipe(
        id=recipe_id,
        agent=agent,
        title="Build a validated form",
        tags=["forms", "validation", "react"],
        use_when="A generated UI contains a data-entry form.",
        inputs=["Approved form requirements"],
        steps=["Use explicit field types", "Validate each field"],
        done_when="The form compiles and validation is covered.",
        pitfalls=["Do not weaken type checking"],
        output="A typed, validated form.",
        version="1.0.0",
        status=status,
    )


def test_lexical_retrieval_is_approved_agent_scoped_and_bounded() -> None:
    recipes = [
        recipe(recipe_id="SKL-CODE-001"),
        recipe(recipe_id="SKL-CODE-002", status="draft"),
        recipe(recipe_id="SKL-CRIT-001", agent="Critic Agent"),
    ]
    registry = SkillRegistry(InMemorySkillRepository(recipes))

    matches = registry.retrieve(agent="Coder Agent", query="React form validation", limit=50)

    assert [item.id for item in matches] == ["SKL-CODE-001"]


class SearchUnavailableRepository(InMemorySkillRepository):
    def search_approved(self, *, agent: str, query: str, limit: int) -> list[SkillRecipe]:
        raise RuntimeError("Search is temporarily unavailable")


def test_search_failure_falls_back_to_approved_lexical_retrieval() -> None:
    registry = SkillRegistry(SearchUnavailableRepository([recipe(recipe_id="SKL-CODE-001")]))

    assert [item.id for item in registry.retrieve(agent="Coder Agent", query="form validation")] == [
        "SKL-CODE-001"
    ]


def test_disabled_azure_search_falls_back_without_error() -> None:
    repository = object.__new__(AzureSkillRepository)
    repository._search_client = None
    assert repository.search_approved(agent="Coder Agent", query="forms") == []


def test_repair_skill_candidate_stays_draft_until_human_approval() -> None:
    registry = SkillRegistry(InMemorySkillRepository([]))
    candidate = registry.prepare_repair_candidate({
        "title": "Use the CRA public entry template",
        "tags": ["cra", "react", "docker"],
        "useWhen": "A generated Create React App Docker build reports public/index.html is missing.",
        "inputs": ["Build log", "Generated package.json"],
        "steps": ["Check the react-scripts build command", "Add public/index.html with the root mount"],
        "doneWhen": "The frontend build succeeds and the container serves HTML at /.",
        "pitfalls": ["Do not change approved application features"],
        "output": "A repeatable CRA packaging correction.",
    })
    assert candidate is not None
    assert candidate.status == "draft"

    saved = registry.save_repair_candidate(candidate, build_id="build-123")
    assert saved.status == "draft"
    assert registry.retrieve(agent="Coder Agent", query="CRA public entry Docker") == []

    registry.decide(saved.id, decision="submit")
    approved = registry.decide(saved.id, decision="approve", reason="Deployment evidence reviewed")
    assert approved.status == "approved"
    assert registry.retrieve(agent="Coder Agent", query="CRA public entry Docker") == [approved]


def test_repair_skill_candidate_rejects_secrets_and_control_bypass_steps() -> None:
    registry = SkillRegistry(InMemorySkillRepository([]))
    candidate = {
        "title": "Unsafe recipe",
        "tags": ["security"],
        "useWhen": "Any task",
        "inputs": ["token"],
        "steps": ["Disable authentication and use api_key=secret-value"],
        "doneWhen": "It works",
        "output": "App",
    }
    assert registry.prepare_repair_candidate(candidate) is None


class MemoryBlob:
    def __init__(self, container: MemoryBlobContainer, name: str) -> None:
        self.container = container
        self.name = name

    def download_blob(self) -> MemoryDownload:
        return MemoryDownload(self.container.items[self.name])


class MemoryDownload:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def readall(self) -> bytes:
        return self.content


class MemoryBlobContainer:
    def __init__(self) -> None:
        self.items: dict[str, bytes] = {}

    def upload_blob(self, *, name: str, data: bytes, overwrite: bool) -> None:
        if name in self.items and not overwrite:
            error = RuntimeError("blob exists")
            error.status_code = 409
            raise error
        self.items[name] = data

    def get_blob_client(self, name: str) -> MemoryBlob:
        return MemoryBlob(self, name)


class MemoryCosmos:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def upsert_item(self, document: dict) -> None:
        self.items[document["id"]] = dict(document)

    def read_item(self, *, item: str, partition_key: str) -> dict:
        return dict(self.items[item])


class MemorySearch:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}
        self.query_options: dict | None = None

    def upload_documents(self, *, documents: list[dict]) -> list:
        for document in documents:
            self.documents[document["skillId"]] = dict(document)
        return [type("UploadResult", (), {"succeeded": True})()]

    def search(self, **options) -> list[dict]:
        self.query_options = options
        return [
            {"skillId": document["skillId"], "version": document["version"]}
            for document in self.documents.values()
            if document["agent"] == "Coder Agent" and document["status"] == "approved"
        ]


def test_azure_skill_repository_round_trips_blob_body_and_search_metadata() -> None:
    repository = object.__new__(AzureSkillRepository)
    repository._body_container = MemoryBlobContainer()
    repository._container = MemoryCosmos()
    repository._partition_field = "skillId"
    repository._search_client = MemorySearch()
    approved = recipe(recipe_id="SKL-CODE-001")

    repository.save(approved)
    stored_metadata = repository._container.items[approved.id]
    assert "steps" not in stored_metadata
    assert stored_metadata["bodyBlobName"].startswith("skill-bodies/SKL-CODE-001/1.0.0/")

    loaded = repository.get(approved.id)
    assert loaded.steps == approved.steps
    assert loaded.status == "approved"

    matches = repository.search_approved(agent="Coder Agent", query="form validation", limit=5)
    assert [item.id for item in matches] == [approved.id]
    assert "status eq 'approved'" in repository._search_client.query_options["filter"]


def test_azure_search_results_cannot_bypass_cosmos_approval_state() -> None:
    repository = object.__new__(AzureSkillRepository)
    repository._body_container = None
    repository._container = MemoryCosmos()
    repository._partition_field = "skillId"
    repository._search_client = MemorySearch()
    pending = recipe(recipe_id="SKL-CODE-002", status="pending_approval")
    repository._container.upsert_item(pending.model_dump(mode="json", by_alias=True))
    repository._search_client.documents[pending.id] = {
        "skillId": pending.id,
        "version": pending.version,
        "agent": pending.agent,
        "status": "approved",
    }

    assert repository.search_approved(agent="Coder Agent", query="form", limit=5) == []