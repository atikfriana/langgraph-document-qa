"""
Embedding model wrapper.

A single function constructs the embedding client so the exact same model
(and only that model) is used at both ingestion time and query time — using
different embedding models for the two would silently corrupt similarity
search results. Now backed by Google's Gemini embedding model instead of
OpenAI's.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    """Return a cached, configured Gemini embeddings client."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model_name,
        # Unlike ChatGoogleGenerativeAI (see app/llm/client.py), the
        # embeddings class did not rename this parameter in the 4.x line --
        # `google_api_key` remains its documented name, so it is left as-is.
        google_api_key=settings.google_api_key,
    )