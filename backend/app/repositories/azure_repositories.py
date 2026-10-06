from __future__ import annotations

import json
import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..models.schemas import BuildState, SkillRecipe

logger = logging.getLogger(__name__)


def _azure_credential() -> Any:
    try:
        from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
    except ImportError as exc:
        raise RuntimeError("Azure persistence is enabled but azure-identity is not installed") from exc

    if os.getenv("AUTOFORGE_IDENTITY_MODE", "").lower() == "managed_identity":
        client_id = os.getenv("AZURE_CLIENT_ID")
        return ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
    return DefaultAzureCredential()


class AzureBuildRepository:
    """Durable build index in Cosmos DB with immutable full-state snapshots in Blob Storage."""

    def __init__(self) -> None:
        endpoint = os.getenv("AUTOFORGE_COSMOS_ENDPOINT", "").strip()
        blob_url = os.getenv("AUTOFORGE_BLOB_ACCOUNT_URL", "").strip()
        if not endpoint or not blob_url:
            raise RuntimeError(
                "Azure persistence requires AUTOFORGE_COSMOS_ENDPOINT and AUTOFORGE_BLOB_ACCOUNT_URL"
            )
        try:
            from azure.cosmos import CosmosClient
            from azure.storage.blob import BlobServiceClient
        except ImportError as exc:
            raise RuntimeError("Azure persistence is enabled but Azure Cosmos/Blob SDKs are not installed") from exc

        self._credential = _azure_credential()
        self._database = CosmosClient(endpoint, credential=self._credential).get_database_client(
            os.getenv("AUTOFORGE_COSMOS_DATABASE", "autoforge")
        )
        self._jobs = self._database.get_container_client(os.getenv("AUTOFORGE_COSMOS_JOBS_CONTAINER", "jobs"))
        self._blob_service = BlobServiceClient(account_url=blob_url, credential=self._credential)
        self._snapshots = self._blob_service.get_container_client(
            os.getenv("AUTOFORGE_BLOB_WORKSPACES_CONTAINER", "workspaces")
        )
        self._intake = self._blob_service.get_container_client(
            os.getenv("AUTOFORGE_BLOB_SPECS_CONTAINER", "specs")
        )
        # Fail during startup when configured resources or permissions are wrong.
        jobs_properties = self._jobs.read()
        self._jobs_partition_field = AzureSkillRepository._partition_field_name(jobs_properties, "jobs")
        self._snapshots.get_container_properties()
        self._intake.get_container_properties()

    def claim_deployment_repair(self, build_id: str, commit: str) -> bool:
        # Immutable claim prevents two API replicas repairing the same commit.
        try:
            self._snapshots.upload_blob(
                name=f"{build_id}/deployment-repairs/{commit}.json",
                data=b'{"claimed":true}', overwrite=False,
            )
        except Exception as exc:
            if getattr(exc, "status_code", None) == 409:
                return False
            raise
        return True

    def save(self, build: BuildState) -> None:
        snapshot_name = f"{build.id}/snapshots/{uuid4().hex}.json"
        payload = build.model_dump(mode="json", by_alias=True)
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._snapshots.upload_blob(name=snapshot_name, data=encoded, overwrite=False)

        # Keep submitted/extracted source in its dedicated container as an immutable intake record.
        intake_name = f"{build.id}/intake.json"
        try:
            self._intake.get_blob_client(intake_name).get_blob_properties()
        except Exception as exc:
            if getattr(exc, "status_code", None) != 404:
                raise
            try:
                self._intake.upload_blob(
                    name=intake_name,
                    data=json.dumps(
                        {
                            "buildId": build.id,
                            "title": build.title,
                            "sourceType": build.source_type,
                            "sourceText": build.source_text,
                            "files": build.files,
                            "recordedAt": datetime.now(timezone.utc).isoformat(),
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8"),
                    overwrite=False,
                )
            except Exception as upload_exc:
                # Concurrent saves can both observe the intake as absent. The
                # first immutable upload wins; any other storage error must surface.
                if getattr(upload_exc, "status_code", None) != 409:
                    raise

        # Existing Cosmos containers can use `/id`, `/jobId`, or another simple
        # key path. Populate its declared path so this adapter fits the provisioned schema.
        document = {
            "id": build.id,
            "jobId": build.id,
            self._jobs_partition_field: build.id,
            "snapshotBlob": snapshot_name,
            "title": build.title,
            "status": build.status,
            "stage": build.stage,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._jobs.upsert_item(document)

    def get(self, build_id: str) -> BuildState:
        try:
            record = self._jobs.read_item(item=build_id, partition_key=build_id)
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                raise KeyError(f"Build '{build_id}' not found") from exc
            raise
        return self._read_snapshot(record["snapshotBlob"])

    def list(self) -> list[BuildState]:
        records = list(
            self._jobs.query_items(
                query="SELECT c.id, c.jobId, c.snapshotBlob, c.updatedAt FROM c WHERE IS_DEFINED(c.snapshotBlob) ORDER BY c.updatedAt DESC",
                enable_cross_partition_query=True,
            )
        )
        return [self._read_snapshot(record["snapshotBlob"]) for record in records]

    def _read_snapshot(self, blob_name: str) -> BuildState:
        content = self._snapshots.get_blob_client(blob_name).download_blob().readall()
        return BuildState.model_validate_json(content)


class AzureSkillRepository:
    """Cosmos governance metadata, Blob recipe bodies, and optional Azure AI Search."""

    def __init__(self) -> None:
        endpoint = os.getenv("AUTOFORGE_COSMOS_ENDPOINT", "").strip()
        if not endpoint:
            raise RuntimeError("Azure skill persistence requires AUTOFORGE_COSMOS_ENDPOINT")
        try:
            from azure.cosmos import CosmosClient
        except ImportError as exc:
            raise RuntimeError("Azure skill persistence is enabled but azure-cosmos is not installed") from exc

        self._credential = _azure_credential()
        database = CosmosClient(endpoint, credential=self._credential).get_database_client(
            os.getenv("AUTOFORGE_COSMOS_DATABASE", "autoforge")
        )
        self._container = database.get_container_client(os.getenv("AUTOFORGE_COSMOS_SKILLS_CONTAINER", "skills"))
        properties = self._container.read()
        self._partition_field = self._partition_field_name(properties, "skills")
        self._body_container = None
        blob_url = os.getenv("AUTOFORGE_BLOB_ACCOUNT_URL", "").strip()
        if blob_url:
            try:
                from azure.storage.blob import BlobServiceClient
            except ImportError as exc:
                raise RuntimeError("Install azure-storage-blob for Azure skill body storage") from exc
            self._body_container = BlobServiceClient(
                account_url=blob_url, credential=self._credential
            ).get_container_client(os.getenv("AUTOFORGE_BLOB_WORKSPACES_CONTAINER", "workspaces"))

        self._search_client = None
        search_endpoint = os.getenv("AUTOFORGE_SKILL_SEARCH_ENDPOINT", "").strip()
        search_index = os.getenv("AUTOFORGE_SKILL_SEARCH_INDEX", "").strip()
        if search_endpoint and search_index:
            try:
                from azure.search.documents import SearchClient
            except ImportError as exc:
                raise RuntimeError("Install azure-search-documents to enable Azure skill search") from exc
            self._search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=search_index,
                credential=self._credential,
            )

    def list(self) -> list[SkillRecipe]:
        documents = self._container.query_items(
            query="SELECT * FROM c", enable_cross_partition_query=True
        )
        return [self._hydrate(self._clean(document)) for document in documents]

    def get(self, recipe_id: str) -> SkillRecipe:
        try:
            document = self._container.read_item(item=recipe_id, partition_key=recipe_id)
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                raise KeyError(f"Skill recipe '{recipe_id}' not found") from exc
            raise
        return self._hydrate(self._clean(document))

    def save(self, recipe: SkillRecipe) -> None:
        document = recipe.model_dump(mode="json", by_alias=True)
        document["skillId"] = recipe.id
        document["id"] = recipe.id
        document[self._partition_field] = recipe.id
        if self._body_container is not None:
            body_keys = ("useWhen", "inputs", "steps", "doneWhen", "pitfalls", "output")
            body = {key: document[key] for key in body_keys}
            encoded_body = json.dumps(body, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
            digest = hashlib.sha256(encoded_body).hexdigest()
            blob_name = f"skill-bodies/{recipe.id}/{recipe.version}/{digest}.json"
            try:
                self._body_container.upload_blob(name=blob_name, data=encoded_body, overwrite=False)
            except Exception as exc:
                if getattr(exc, "status_code", None) != 409:
                    raise
            for key in body_keys:
                document.pop(key, None)
            document["bodyBlobName"] = blob_name
            document["bodySha256"] = digest

        self._sync_search_document(recipe)
        self._container.upsert_item(document)

    def search_approved(self, *, agent: str, query: str, limit: int = 5) -> list[SkillRecipe]:
        if self._search_client is None:
            return []
        escaped_agent = agent.replace("'", "''")
        matches = self._search_client.search(
            search_text=query.strip() or "*",
            search_fields=["title", "tags", "useWhen", "searchText"],
            filter=f"agent eq '{escaped_agent}' and status eq 'approved'",
            select=["skillId", "version"],
            top=max(1, min(limit, 5)),
        )
        recipes: list[SkillRecipe] = []
        for match in matches:
            recipe_id = match.get("skillId")
            if not isinstance(recipe_id, str):
                continue
            try:
                recipe = self.get(recipe_id)
            except KeyError:
                continue
            if recipe.status == "approved" and recipe.agent.lower() == agent.lower() and recipe.version == match.get("version"):
                recipes.append(recipe)
        return recipes

    def _sync_search_document(self, recipe: SkillRecipe) -> None:
        if self._search_client is None:
            return
        document = {
            "id": recipe.id,
            "skillId": recipe.id,
            "version": recipe.version,
            "agent": recipe.agent,
            "title": recipe.title,
            "tags": recipe.tags,
            "status": recipe.status,
            "useWhen": recipe.use_when,
            "searchText": " ".join([
                recipe.title, recipe.use_when, *recipe.tags, *recipe.inputs,
                *recipe.steps, *recipe.pitfalls, recipe.done_when, recipe.output,
            ]),
        }
        try:
            result = self._search_client.upload_documents(documents=[document])
            if result and not all(item.succeeded for item in result):
                logger.warning("Azure AI Search rejected a skill index update for %s", recipe.id)
        except Exception:
            # Cosmos remains authoritative; approved-only lexical retrieval is the fallback.
            logger.exception("Azure AI Search skill indexing failed for %s", recipe.id)

    def _hydrate(self, document: dict[str, Any]) -> SkillRecipe:
        blob_name = document.get("bodyBlobName")
        if blob_name and self._body_container is not None:
            content = self._body_container.get_blob_client(blob_name).download_blob().readall()
            body = json.loads(content.decode("utf-8"))
            document = {**document, **body}
        return SkillRecipe.model_validate(document)

    def backfill(self) -> None:
        """Migrate legacy full Cosmos recipes and populate an enabled Search index."""
        if self._body_container is None and self._search_client is None:
            return
        try:
            recipes = self.list()
            for recipe in recipes:
                self.save(recipe)
        except Exception:
            # A cloud-search outage must not prevent builds; retrieval remains lexical.
            logger.exception("Skill Blob/Search backfill failed; retaining Cosmos-backed retrieval")

    @staticmethod
    def _partition_field_name(properties: dict[str, Any], container: str) -> str:
        paths = properties.get("partitionKey", {}).get("paths", [])
        if len(paths) != 1 or not paths[0].startswith("/") or "/" in paths[0][1:]:
            raise RuntimeError(
                f"Cosmos container '{container}' must use one simple partition key path, such as /jobId or /skillId"
            )
        return paths[0][1:]

    @staticmethod
    def _clean(document: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in document.items() if not key.startswith("_") and key != "_rid"}
