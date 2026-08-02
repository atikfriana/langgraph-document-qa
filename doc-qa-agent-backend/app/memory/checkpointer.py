"""
Checkpointer factory for LangGraph conversation memory.

Returns a `MemorySaver` for local/dev by default, and a `SqliteSaver` when
configured for a persistent backend — selected purely by config, per Phase 1's
"pluggable checkpointer" design decision. Callers never construct a
checkpointer directly; they always go through `get_checkpointer()`.
"""

from __future__ import annotations

import sqlite3
from functools import lru_cache

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from app.config import settings


class UnsupportedCheckpointerBackendError(ValueError):
    """Raised when `settings.checkpointer_backend` names an unknown backend."""


@lru_cache(maxsize=1)
def get_checkpointer() -> BaseCheckpointSaver:
    """Return a process-wide checkpointer instance for graph compilation."""
    backend = settings.checkpointer_backend.lower()

    if backend == "memory":
        return MemorySaver()

    if backend == "sqlite":
        settings.sqlite_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            str(settings.sqlite_checkpoint_path), check_same_thread=False
        )
        return SqliteSaver(connection)

    raise UnsupportedCheckpointerBackendError(
        f"Unknown checkpointer backend '{backend}'. Expected 'memory' or 'sqlite'."
    )