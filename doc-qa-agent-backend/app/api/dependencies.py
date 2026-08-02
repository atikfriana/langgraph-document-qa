"""
FastAPI dependency-injection providers.

Every route depends on abstractions obtained through `Depends(...)` here
rather than importing/constructing collaborators directly — this is the
Dependency Inversion piece of SOLID applied to the API layer, and it's what
lets routes be tested with fake graphs/vector stores without monkeypatching
imports.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request

from app.core.exceptions import VectorStoreUnavailableError
from app.retrieval.vector_store import VectorStoreClient


def get_compiled_graph(request: Request) -> Any:
    """Return the compiled LangGraph agent stored on `app.state` at startup."""
    return request.app.state.agent_graph


def get_vector_store_client(request: Request) -> VectorStoreClient:
    """Return the shared vector store client, raising if not yet loaded."""
    client: VectorStoreClient | None = getattr(
        request.app.state, "vector_store_client", None
    )
    if client is None or not client.is_loaded:
        raise VectorStoreUnavailableError(
            "Vector store is not loaded. Run ingestion and restart the service."
        )
    return client