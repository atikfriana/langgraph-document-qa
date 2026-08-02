"""
Tool-decision (routing) node.

Calls the chat model with the web search tool bound, per the strategy
described in Phase 1 Section 7 and encoded in `ROUTER_PROMPT`. The model's
response either contains `tool_calls` (routed to `tool_exec`) or not
(routed straight to `generate`) — the actual routing happens in
`app.graph.edges`, this node only produces the decision.

This node always runs (retrieve -> decide_tool is an unconditional edge),
so it is also the correct place to reset the per-turn `tool_result` field.
Without this reset, a turn that does NOT call the tool would otherwise keep
whatever `tool_result` value was checkpointed from an earlier turn in the
same thread (LangGraph only overwrites a state field when some node in the
current run actually returns it) — `tool_exec_node` is skipped entirely on
non-tool turns, so nothing else in the graph would ever clear it.
"""

from __future__ import annotations

from app.graph.prompts import ROUTER_PROMPT
from app.graph.state import AgentState
from app.llm.client import bind_tools_to_model, get_chat_model
from app.tools.web_search_tool import AGENT_TOOLS


def _format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as plain text for prompt injection."""
    if not chunks:
        return "No relevant context was found in the source document."

    return "\n\n".join(
        f"[source: {chunk['source']} | score: {chunk['score']:.2f}]\n{chunk['content']}"
        for chunk in chunks
    )


def decide_tool_node(state: AgentState) -> dict:
    """Ask the model whether the web search tool is needed for this turn."""
    model = bind_tools_to_model(get_chat_model(), AGENT_TOOLS)
    context_text = _format_context(state.get("retrieved_context", []))

    prompt_messages = ROUTER_PROMPT.format_messages(
        context=context_text,
        messages=state["messages"],
    )
    response = model.invoke(prompt_messages)

    # Reset tool_result unconditionally on every turn. If this turn ends up
    # calling the tool, tool_exec_node runs afterward and overwrites this
    # with the real result; if not, this None is what persists — never a
    # stale value from a previous turn.
    return {"messages": [response], "tool_result": None}