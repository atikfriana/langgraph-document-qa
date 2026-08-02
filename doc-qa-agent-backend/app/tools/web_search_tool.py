"""
Single external tool: web search.

Implemented via Tavily's search API (purpose-built for LLM tool use — returns
clean, citation-ready snippets rather than raw HTML). Exposed as a single
`@tool`-decorated function so it can be bound directly to the chat model's
function-calling schema; the docstring IS the interface the LLM reads to
decide relevance, so it is written precisely.
"""

from __future__ import annotations

import logging

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from app.config import settings

logger = logging.getLogger(__name__)


class WebSearchUnavailableError(RuntimeError):
    """Raised when the web search tool is invoked without an API key configured."""


def _get_search_client() -> TavilySearch:
    if not settings.tavily_api_key:
        raise WebSearchUnavailableError(
            "TAVILY_API_KEY is not configured; web search tool cannot run."
        )
    return TavilySearch(api_key=settings.tavily_api_key, max_results=3)


@tool
def web_search(query: str) -> str:
    """Search the public web for current or external information that is NOT
    contained in the agent's source document — for example, recent news,
    live data, or facts about topics the document does not cover.

    Args:
        query: A concise, well-formed search query describing what to look up.

    Returns:
        A short, plain-text summary of the most relevant web search results.
    """
    try:
        client = _get_search_client()
        raw_results = client.invoke({"query": query})
    except WebSearchUnavailableError:
        logger.warning("Web search invoked but no API key is configured.")
        return "Web search is currently unavailable."
    except Exception:  # noqa: BLE001 - tool failures must not crash the graph
        logger.exception("Web search call failed for query=%r", query)
        return "Web search failed to return results for this query."

    results = raw_results.get("results", []) if isinstance(raw_results, dict) else []
    if not results:
        return "No relevant web search results were found."

    formatted = "\n".join(
        f"- {item.get('title', 'Untitled')}: {item.get('content', '')}"
        for item in results
    )
    return formatted


AGENT_TOOLS = [web_search]