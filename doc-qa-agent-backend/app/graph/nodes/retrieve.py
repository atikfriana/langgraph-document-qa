"""
Retrieval node.

Always the first node in the graph (per Phase 1 Section 3). Embeds the
latest human message and queries the vector store, writing results into the
per-turn `retrieved_context` field. Deliberately does not touch `messages`
or `tool_result` — this node has exactly one responsibility.
"""
from __future__ import annotations

from dataclasses import asdict


from langchain_core.messages import HumanMessage

from app.graph.state import AgentState
from app.retrieval.vector_store import get_vector_store_client


def _latest_human_message_content(state: AgentState) -> str:
    """Return the text of the most recent human message in state."""
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def retrieve_node(state: AgentState) -> dict:
    """Retrieve top-k document chunks relevant to the latest user message."""
    query = _latest_human_message_content(state)
    if not query.strip():
        return {"retrieved_context": []}

    client = get_vector_store_client()
    chunks = client.similarity_search(query)

    return {
    "retrieved_context": [asdict(chunk) for chunk in chunks]
}