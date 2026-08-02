"""
Tool execution node.

Runs whichever tool call(s) the `decide_tool` node's AI message requested,
appends the corresponding `ToolMessage`(s) to conversation history (required
by OpenAI's function-calling protocol), and also writes a plain-text summary
into the per-turn `tool_result` field so `generate` and the API layer's
`tool_used` flag can consume it without re-parsing message history.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from app.graph.state import AgentState
from app.tools.web_search_tool import AGENT_TOOLS

logger = logging.getLogger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in AGENT_TOOLS}


def _execute_single_tool_call(tool_call: dict[str, Any]) -> ToolMessage:
    """Execute one tool call and wrap its output as a `ToolMessage`."""
    tool_name = tool_call["name"]
    tool = _TOOLS_BY_NAME.get(tool_name)

    if tool is None:
        logger.warning("Model requested unknown tool: %s", tool_name)
        content = f"Error: tool '{tool_name}' is not available."
    else:
        try:
            content = str(tool.invoke(tool_call["args"]))
        except Exception:  # noqa: BLE001 - a failed tool must not crash the graph
            logger.exception("Tool '%s' raised during execution", tool_name)
            content = f"Error: tool '{tool_name}' failed to execute."

    return ToolMessage(content=content, tool_call_id=tool_call["id"])


def tool_exec_node(state: AgentState) -> dict:
    """Execute the pending tool call(s) from the latest AI message."""
    last_message = state["messages"][-1]
    tool_calls = (
        last_message.tool_calls if isinstance(last_message, AIMessage) else None
    ) or []

    if not tool_calls:
        return {"tool_result": None}

    tool_messages = [_execute_single_tool_call(call) for call in tool_calls]
    combined_result = "\n".join(str(msg.content) for msg in tool_messages)

    return {
        "messages": tool_messages,
        "tool_result": combined_result,
    }