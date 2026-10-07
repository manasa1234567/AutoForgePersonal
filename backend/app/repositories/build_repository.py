from __future__ import annotations

from typing import Protocol

from ..models.schemas import BuildState


class BuildRepository(Protocol):
    """Storage contract for build records."""

    def save(self, build: BuildState) -> None: ...

    def get(self, build_id: str) -> BuildState: ...

    def list(self) -> list[BuildState]: ...

    def claim_deployment_repair(self, build_id: str, commit: str) -> bool: ...
    def get_preview(self, build_id: str, digest: str) -> dict | None: ...
    def save_preview(self, build_id: str, digest: str, value: dict) -> None: ...


class InMemoryBuildRepository:
    """Development-only repository. Records disappear when the API process restarts."""

    def __init__(self) -> None:
        self._items: dict[str, BuildState] = {}
        self._deployment_claims: set[tuple[str, str]] = set()
        self._previews: dict[tuple[str, str], dict] = {}

    def get_preview(self, build_id: str, digest: str) -> dict | None:
        return self._previews.get((build_id, digest))

    def save_preview(self, build_id: str, digest: str, value: dict) -> None:
        self._previews[(build_id, digest)] = value

    def claim_deployment_repair(self, build_id: str, commit: str) -> bool:
        key = (build_id, commit)
        if key in self._deployment_claims:
            return False
        self._deployment_claims.add(key)
        return True

    def save(self, build: BuildState) -> None:
        self._items[build.id] = build

    def get(self, build_id: str) -> BuildState:
        try:
            return self._items[build_id]
        except KeyError as exc:
            raise KeyError(f"Build '{build_id}' not found") from exc

    def list(self) -> list[BuildState]:
        return list(self._items.values())[::-1]


def build_repository_from_environment() -> BuildRepository:
    """Select durable Azure storage only when explicitly enabled."""
    import os

    if os.getenv("AUTOFORGE_PERSISTENCE", "local").strip().lower() == "azure":
        from .azure_repositories import AzureBuildRepository

        return AzureBuildRepository()
    return InMemoryBuildRepository()
