"""
FAISS vector store initialization and query interface.

Wraps FAISS behind a small interface (`VectorStoreClient`) rather than
exposing the raw LangChain `FAISS` object to callers — this is the
Dependency Inversion piece of SOLID: the `retrieve` node depends on this
abstraction, not on FAISS specifics, so the backing store can later be
swapped (e.g. for a managed/production vector DB) by changing only this file.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.models import RetrievedChunk
from app.retrieval.embeddings import get_embeddings_model


class VectorStoreNotBuiltError(RuntimeError):
    """Raised when a query is attempted before the index has been built."""


class VectorStoreDimensionMismatchError(RuntimeError):
    """Raised when a persisted index's vector dimension does not match the
    currently configured embedding model.

    This happens when the embedding provider/model is changed (e.g. during
    a migration) without re-running ingestion against the new model. FAISS
    does not validate this on load, so without this check the mismatch would
    otherwise surface as either an opaque numpy/FAISS shape error, or worse,
    silently wrong similarity results with no error at all.
    """


class VectorStoreClient:
    """Thin façade over a persisted FAISS index."""

    def __init__(self, store_dir: Path | None = None) -> None:
        self._store_dir = store_dir or settings.vector_store_dir
        self._store: FAISS | None = None

    @property
    def store_dir(self) -> Path:
        """Public accessor for the index directory (avoids private-attribute
        access from other modules, e.g. `app.retrieval.ingest`)."""
        return self._store_dir

    @property
    def is_loaded(self) -> bool:
        return self._store is not None

    def build_from_documents(self, documents: list[Document]) -> None:
        """Build a fresh FAISS index from chunked documents and persist it."""
        if not documents:
            raise ValueError("Cannot build a vector store from zero documents.")

        embeddings = get_embeddings_model()
        self._store = FAISS.from_documents(documents, embeddings)
        self._store_dir.mkdir(parents=True, exist_ok=True)
        self._store.save_local(str(self._store_dir))

    def load(self) -> None:
        """Load a previously persisted FAISS index from disk.

        Validates that the index's stored vector dimension matches what the
        currently configured embedding model produces, failing fast with a
        clear, actionable error instead of allowing a silent mismatch to
        reach query time.
        """
        if not self._store_dir.exists():
            raise VectorStoreNotBuiltError(
                f"No vector store found at {self._store_dir}. "
                "Run the ingestion script first."
            )
        embeddings = get_embeddings_model()
        store = FAISS.load_local(
            str(self._store_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        self._validate_embedding_dimension(store, embeddings)
        self._store = store

    def _validate_embedding_dimension(self, store: FAISS, embeddings) -> None:
        """Compare the persisted index's vector width against a live probe
        embedding from the currently configured model."""
        index_dimension = store.index.d
        probe_vector = embeddings.embed_query("dimension consistency probe")
        configured_dimension = len(probe_vector)

        if index_dimension != configured_dimension:
            raise VectorStoreDimensionMismatchError(
                f"Persisted FAISS index at '{self._store_dir}' has dimension "
                f"{index_dimension}, but the configured embedding model "
                f"'{settings.embedding_model_name}' produces "
                f"{configured_dimension}-dimensional vectors. The index was "
                "likely built with a different embedding model (e.g. before "
                "a provider migration). Run `python scripts/run_ingest.py` "
                "to rebuild it against the current model."
            )

    def similarity_search(
        self, query: str, top_k: int | None = None
    ) -> list[RetrievedChunk]:
        """Return the top-k most similar chunks to `query`, with scores."""
        if self._store is None:
            raise VectorStoreNotBuiltError(
                "Vector store accessed before load()/build_from_documents()."
            )

        k = top_k or settings.retrieval_top_k
        results = self._store.similarity_search_with_relevance_scores(query, k=k)

        return [
            RetrievedChunk(
                content=doc.page_content,
                source=str(doc.metadata.get("source", "unknown")),
                chunk_id=str(doc.metadata.get("chunk_id", idx)),
                score=float(score),
            )
            for idx, (doc, score) in enumerate(results)
        ]


_default_client: VectorStoreClient | None = None


def get_vector_store_client() -> VectorStoreClient:
    """Return a process-wide singleton vector store client, loading it lazily."""
    global _default_client
    if _default_client is None:
        _default_client = VectorStoreClient()
        _default_client.load()
    return _default_client