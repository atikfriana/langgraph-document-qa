"""
LangGraph state definition.

`AgentState` is the single object threaded through every node. Per Phase 1
design: `messages` is the only field that accumulates across turns (managed
by the checkpointer); `retrieved_context` and `tool_result` are per-turn and
are deliberately overwritten each invocation, never appended, so stale
context from earlier turns cannot leak into the current answer.
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    messages: Annotated[list[AnyMessage], add_messages]
    """Full conversation history. Reducer-managed — nodes return only new
    messages to append, never the full list."""

    retrieved_context: list[dict[str, Any]]
    """Document chunks retrieved for the *current* turn only."""

    tool_result: str | None
    """Output of the tool call made this turn, if any. Reset each turn."""

    session_id: str
    """Identifies the conversation thread (mirrors the checkpointer thread_id)."""