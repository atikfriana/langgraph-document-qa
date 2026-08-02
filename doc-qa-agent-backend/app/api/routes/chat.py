"""
Chat endpoint: the sole entry point for conversing with the agent.

Route handlers stay thin — they validate input, invoke the LangGraph agent
via dependency injection, and shape the output. All actual decision-making
(retrieval, tool routing, generation) lives in the graph layer, not here.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from app.api.dependencies import get_compiled_graph
from app.core.exceptions import GraphExecutionError, InvalidRequestError
from app.memory.session_store import build_thread_config, generate_session_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Incoming chat message from a client."""

    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(
        default=None,
        description="Existing session id to continue a conversation. "
        "Omit to start a new session.",
    )


class SourceReference(BaseModel):
    """A document chunk that informed the answer, surfaced for transparency."""

    source: str
    chunk_id: str
    score: float


class ChatResponse(BaseModel):
    """Final answer returned to the client."""

    session_id: str
    response: str
    tool_used: bool
    sources: list[SourceReference]


def _extract_sources(chunks: list[dict]) -> list[SourceReference]:
    """Convert retrieved_context dictionaries into API response objects."""
    return [
        SourceReference(
            source=c["source"],
            chunk_id=c["chunk_id"],
            score=float(c["score"]),
        )
        for c in chunks
    ]


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    payload: ChatRequest,
    graph: Annotated[Any, Depends(get_compiled_graph)],
) -> ChatResponse:
    """Send a message to the agent and receive its answer for this turn."""
    if not payload.message.strip():
        raise InvalidRequestError("message must not be blank.")

    session_id = payload.session_id or generate_session_id()
    thread_config = build_thread_config(session_id)

    try:
        result_state = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=payload.message)],
                "session_id": session_id,
            },
            config=thread_config,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Graph execution failed for session_id=%s", session_id)
        raise GraphExecutionError(
            "The agent failed to produce a response.",
            session_id=session_id,
        ) from exc

    messages = result_state.get("messages", [])
    final_ai_message = next(
        (m for m in reversed(messages) if isinstance(m, AIMessage)),
        None,
    )

    if final_ai_message is None:
        raise GraphExecutionError(
            "The agent did not produce a final answer.",
            session_id=session_id,
        )

    tool_result = result_state.get("tool_result")
    retrieved_chunks = result_state.get("retrieved_context", [])

    return ChatResponse(
        session_id=session_id,
        # `.text` (not `str(.content)`) is required as of Gemini 3: these
        # models return `content` as a list of typed content blocks (to
        # carry the thought_signature alongside any text/tool-call parts)
        # rather than a plain string. `.text` is langchain-core's
        # provider-agnostic accessor that concatenates just the text blocks
        # regardless of which shape `content` is in -- `str(.content)` would
        # instead stringify the raw block list (e.g. "[{'type': 'text', ...}]")
        # into the API response.
        response=final_ai_message.text,
        tool_used=tool_result is not None,
        sources=_extract_sources(retrieved_chunks),
    )