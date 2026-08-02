"""
Tests for the retrieval layer: chunking and the FAISS vector store façade.

Chunking is tested against real `RecursiveCharacterTextSplitter` behavior
(no network calls involved). Vector store tests use a stubbed embeddings
model so no OpenAI API call is made, while still exercising real FAISS
indexing/search logic — this validates the actual similarity-search
integration, not just our wrapper code.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from app.models import RetrievedChunk
from app.retrieval.loader import UnsupportedDocumentTypeError, chunk_documents
from app.retrieval.vector_store import VectorStoreClient, VectorStoreNotBuiltError


class TestChunkDocuments:
    def test_splits_long_document_into_multiple_chunks(self) -> None:
        long_text = "Sentence about robots. " * 200
        documents = [Document(page_content=long_text, metadata={"source": "doc.pdf"})]

        chunks = chunk_documents(documents)

        assert len(chunks) > 1
        assert all(len(chunk.page_content) > 0 for chunk in chunks)

    def test_preserves_source_metadata_across_chunks(self) -> None:
        documents = [
            Document(page_content="Short content.", metadata={"source": "doc.pdf"})
        ]

        chunks = chunk_documents(documents)

        assert all(chunk.metadata.get("source") == "doc.pdf" for chunk in chunks)

    def test_empty_document_list_returns_empty_chunks(self) -> None:
        assert chunk_documents([]) == []


class TestVectorStoreClient:
    def test_query_before_load_raises(self) -> None:
        client = VectorStoreClient(store_dir=None)

        with pytest.raises(VectorStoreNotBuiltError):
            client.similarity_search("what is the battery life?")

    def test_build_from_empty_documents_raises(self) -> None:
        client = VectorStoreClient()

        with pytest.raises(ValueError):
            client.build_from_documents([])

    def test_build_and_search_returns_retrieved_chunks(self, tmp_path) -> None:
        fake_embeddings = _FakeEmbeddings()

        with patch(
            "app.retrieval.vector_store.get_embeddings_model",
            return_value=fake_embeddings,
        ):
            client = VectorStoreClient(store_dir=tmp_path / "index")
            documents = [
                Document(
                    page_content="The Aurora M1 has a 10 hour battery life.",
                    metadata={"source": "doc.pdf", "chunk_id": 0},
                ),
                Document(
                    page_content="The company was founded in Denver in 2018.",
                    metadata={"source": "doc.pdf", "chunk_id": 1},
                ),
            ]
            client.build_from_documents(documents)

            results = client.similarity_search("battery life", top_k=1)

        assert len(results) == 1
        assert isinstance(results[0], RetrievedChunk)
        assert "battery" in results[0].content.lower()
        assert results[0].source == "doc.pdf"

    def test_load_missing_index_raises(self, tmp_path) -> None:
        client = VectorStoreClient(store_dir=tmp_path / "does-not-exist")

        with pytest.raises(VectorStoreNotBuiltError):
            client.load()


class _FakeEmbeddings:
    """Deterministic pseudo-embeddings, avoiding real OpenAI API calls.

    Produces fixed-length vectors derived from simple text features so
    semantically different texts land at different points in vector space —
    enough for FAISS similarity search to behave meaningfully in tests.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(text: str) -> list[float]:
        lowered = text.lower()
        return [
            float(lowered.count("battery")),
            float(lowered.count("founded")),
            float(lowered.count("denver")),
            float(len(lowered) % 7),
        ]