"""
Domain models shared across layers (retrieval, memory, graph, tools).

These are plain, framework-agnostic data structures — deliberately kept
independent from LangChain/LangGraph message types and from FastAPI request/
response schemas. This is the Clean Architecture "entities" layer: the core
shapes of data the business logic operates on, which higher layers adapt
to/from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Role(str, Enum):
    """Speaker role for a conversation turn."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A single piece of document context returned by the retriever."""

    content: str
    source: str
    chunk_id: str
    score: float

    @property
    def is_confident(self) -> bool:
        """Whether this chunk is similar enough to be trusted as context."""
        return self.score >= 0.0  # threshold applied at the retriever boundary


@dataclass(frozen=True, slots=True)
class ToolInvocation:
    """Record of a tool call the agent made during a turn."""

    tool_name: str
    tool_input: str
    tool_output: str


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    """A single completed turn, used for logging/observability, not for state."""

    session_id: str
    user_message: str
    assistant_message: str
    retrieved_chunks: tuple[RetrievedChunk, ...] = field(default_factory=tuple)
    tool_invocation: ToolInvocation | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def used_tool(self) -> bool:
        return self.tool_invocation is not None