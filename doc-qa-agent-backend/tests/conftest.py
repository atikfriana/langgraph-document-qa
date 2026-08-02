"""
Shared pytest fixtures.

Fixtures here provide fakes/stubs for expensive external dependencies
(Gemini, FAISS, Tavily) so unit and API tests run deterministically, offline,
and fast — no real API calls are made in the test suite. This follows the
Dependency Inversion pattern established in `app/api/dependencies.py`: tests
inject fakes through the same seams the app uses for real collaborators.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage

# Ensure required env vars exist before any app module is imported, since
# `Settings` validates eagerly at import time via `get_settings()`.
os.environ.setdefault("GOOGLE_API_KEY", "test-google-key-not-real")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_JSON", "false")
os.environ.setdefault("CHECKPOINTER_BACKEND", "memory")

from app.models import RetrievedChunk  # noqa: E402


@pytest.fixture
def sample_retrieved_chunks() -> list[RetrievedChunk]:
    """A small, realistic set of retrieved document chunks for tests."""
    return [
        RetrievedChunk(
            content=(
                "Aurora Robotics was founded in 2018 and manufactures the "
                "Aurora M1 warehouse picking robot."
            ),
            source="sample_document.pdf",
            chunk_id="0",
            score=0.91,
        ),
        RetrievedChunk(
            content=(
                "The Aurora M1 has a battery life of 10 hours and a maximum "
                "payload of 25 kilograms."
            ),
            source="sample_document.pdf",
            chunk_id="1",
            score=0.87,
        ),
    ]


@pytest.fixture
def fake_vector_store_client(sample_retrieved_chunks: list[RetrievedChunk]) -> MagicMock:
    """A stand-in for `VectorStoreClient` that returns canned chunks."""
    client = MagicMock()
    client.is_loaded = True
    client.similarity_search.return_value = sample_retrieved_chunks
    return client


@pytest.fixture
def fake_compiled_graph() -> MagicMock:
    """A stand-in for the compiled LangGraph agent used by the /chat route.

    `ainvoke` mimics a full turn: it echoes back the user's message plus a
    scripted assistant answer, so route-level tests can assert on response
    shaping without exercising real LLM/graph logic.
    """
    graph = MagicMock()

    async def _ainvoke(input_state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        user_message = input_state["messages"][-1]
        answer = AIMessage(content=f"Answer to: {user_message.content}")
        return {
            "messages": [HumanMessage(content=user_message.content), answer],
            "retrieved_context": [],
            "tool_result": None,
            "session_id": input_state.get("session_id", "test-session"),
        }

    graph.ainvoke.side_effect = _ainvoke
    return graph


@pytest.fixture
def app_client(
    fake_compiled_graph: MagicMock, fake_vector_store_client: MagicMock
) -> Generator[TestClient, None, None]:
    """A TestClient wired to fakes instead of real graph/vector-store singletons.

    Bypasses the FastAPI `lifespan` (which would try to load a real FAISS
    index and compile a real graph) by injecting fakes directly into
    `app.state`, matching exactly what `lifespan` would have set.
    """
    from app.api.main import app

    app.state.agent_graph = fake_compiled_graph
    app.state.vector_store_client = fake_vector_store_client

    with TestClient(app) as client:
        yield client