"""
Factory for Gemini-backed LangChain chat models.

Centralizing model construction (SRP) means every node gets a consistently
configured client, and swapping providers/models later touches one file —
this is exactly that swap: OpenAI -> Google Gemini, with the rest of the
graph/API layers untouched since they only depend on the `BaseChatModel`
interface returned here.

Gemini 3 tool-calling note: `langchain-google-genai` >= 4.x captures the
`thought_signature` Gemini 3 attaches to every function-call part and
automatically re-attaches it (via `additional_kwargs`) whenever the *same*
`AIMessage` object is sent back to the model. No special configuration is
needed here for that -- it works because this project already passes the
original checkpointed message objects straight through the graph
(`app/graph/state.py`'s `add_messages` reducer, `generate.py`) instead of
ever reconstructing an `AIMessage` by hand. Reconstructing one manually
anywhere in this codebase would silently drop the signature and reintroduce
the exact 400 error this migration fixes.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


@lru_cache(maxsize=1)
def get_chat_model() -> BaseChatModel:
    print("=" * 50)
    print("MODEL:", settings.chat_model_name)
    print("=" * 50)

    return ChatGoogleGenerativeAI(
        model=settings.chat_model_name,
        temperature=settings.llm_temperature,
        # `api_key` is the current parameter name as of langchain-google-genai
        # 4.x (it now fronts both the Gemini Developer API and Vertex AI).
        # `google_api_key` is still accepted as a backward-compatible alias,
        # but `api_key` is the documented, forward-compatible spelling.
        api_key=settings.google_api_key,
        timeout=30,
        max_retries=2,
    )


def bind_tools_to_model(
    model: BaseChatModel, tools: list[BaseTool]
) -> BaseChatModel:
    """Return a copy of `model` with function-calling tools bound.

    Kept as a standalone function (rather than inlined in a node) so any
    node that needs a tool-aware model uses the exact same binding logic.
    Unchanged by the provider migration — `bind_tools` is a standard
    LangChain `BaseChatModel` method that `ChatGoogleGenerativeAI` also
    implements, so no caller of this function needed to change.
    """
    return model.bind_tools(tools)