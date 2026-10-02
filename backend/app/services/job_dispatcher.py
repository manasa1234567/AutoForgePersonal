from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol


BuildHandler = Callable[[str], Awaitable[None]]


class BuildJobDispatcher(Protocol):
    """Queue contract for starting a build workflow by ID."""

    async def enqueue(self, build_id: str) -> None: ...


class InProcessBuildJobDispatcher:
    """Local-only dispatcher. A Service Bus adapter can implement the same contract."""

    def __init__(self, handler: BuildHandler) -> None:
        self._handler = handler

    async def enqueue(self, build_id: str) -> None:
        asyncio.create_task(self._handler(build_id))
