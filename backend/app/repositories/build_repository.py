from __future__ import annotations

from typing import Protocol

from ..models.schemas import BuildState


class BuildRepository(Protocol):
    """Storage contract for build records."""

    def save(self, build: BuildState) -> None: ...

    def get(self, build_id: str) -> BuildState: ...

    def list(self) -> list[BuildState]: ...


class InMemoryBuildRepository:
    """Development-only repository. Records disappear when the API process restarts."""

    def __init__(self) -> None:
        self._items: dict[str, BuildState] = {}

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
