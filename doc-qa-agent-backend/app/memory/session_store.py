"""
Session/thread identity management.

Keeps the mapping between a client-facing `session_id` and the LangGraph
`thread_id` config key in one place. Currently a 1:1 passthrough, but
isolating it means the mapping can change (e.g., namespacing thread ids per
user) without touching the graph or API layers.
"""

from __future__ import annotations

import uuid
from typing import Any


def generate_session_id() -> str:
    """Generate a new, unique session identifier."""
    return str(uuid.uuid4())


def build_thread_config(session_id: str) -> dict[str, Any]:
    """Build the LangGraph `config` dict that binds a run to a memory thread."""
    if not session_id or not session_id.strip():
        raise ValueError("session_id must be a non-empty string.")

    return {"configurable": {"thread_id": session_id}}