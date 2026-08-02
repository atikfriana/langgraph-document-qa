"""
Conditional edge functions.

LangGraph routes based on plain functions of state that return the name of
the next node — kept separate from node implementations so routing policy
(Phase 1 Section 7: "call the tool only when necessary") is readable in one
place, independent of how the decision was computed.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from app.graph.state import AgentState

NODE_TOOL_EXEC = "tool_exec"
NODE_GENERATE = "generate"


def route_after_decide_tool(state: AgentState) -> str:
    """Route to `tool_exec` if the router requested a tool, else `generate`."""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return NODE_TOOL_EXEC

    return NODE_GENERATE