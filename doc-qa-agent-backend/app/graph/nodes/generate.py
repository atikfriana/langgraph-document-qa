"""
Final answer generation node.

The only node that produces the user-facing message (Phase 1 Section 3).
Synthesizes conversation history, retrieved document context, and any tool
result into a single grounded answer via `GENERATION_PROMPT`.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage

from app.graph.prompts import GENERATION_PROMPT
from app.graph.state import AgentState
from app.llm.client import get_chat_model

logger = logging.getLogger(__name__)


def _format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as plain text for prompt injection."""
    if not chunks:
        return "No relevant context was found in the source document."

    return "\n\n".join(
        f"[source: {chunk['source']} | score: {float(chunk['score']):.2f}]\n{chunk['content']}"
        for chunk in chunks
    )


def _messages_for_generation(messages: list) -> list:
    """Return the message list to send to Gemini for final generation.

    `decide_tool_node` always runs immediately before this node and always
    appends exactly one AIMessage to state["messages"]. When the router
    decided NOT to call the tool, that AIMessage carries a real, complete
    answer with no tool_calls -- leaving it in the history would make the
    conversation end on an assistant turn instead of the user's question,
    which is precisely what causes Gemini to return an empty completion
    (finish_reason=STOP, output_tokens=0): there is nothing new to respond
    to. Excluding that single trailing message restores a conversation that
    ends on a Human turn (no tool call) or a Tool turn (tool call happened),
    both of which are valid states for Gemini to generate a next turn from.

    This only affects what THIS call sends to the model -- state["messages"]
    itself (and therefore checkpointed memory) is untouched, since this
    function never mutates or returns state.
    """
    if messages and isinstance(messages[-1], AIMessage) and not messages[-1].tool_calls:
        return messages[:-1]
    return messages


def generate_node(state: AgentState) -> dict:
    """Produce the final assistant response for this turn."""
    model = get_chat_model()

    context_text = _format_context(state.get("retrieved_context", []))
    tool_result_text = state.get("tool_result") or "No web search was performed."

    prompt_messages = GENERATION_PROMPT.format_messages(
        context=context_text,
        tool_result=tool_result_text,
        messages=_messages_for_generation(state["messages"]),
    )

    response = model.invoke(prompt_messages)

    logger.debug(
        "generation response",
        extra={
            # `.text` (not `.content`): Gemini 3 returns `content` as a list
            # of typed content blocks rather than a plain string, so
            # `len(response.content or "")` would log a block count (e.g. 1
            # or 2) instead of the answer's character length. `.text`
            # concatenates just the text blocks regardless of provider.
            "content_length": len(response.text),
            "response_metadata": response.response_metadata,
        },
    )

    return {"messages": [response]}