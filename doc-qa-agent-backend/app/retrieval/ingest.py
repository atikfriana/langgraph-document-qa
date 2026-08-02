"""
Offline ingestion pipeline: load -> chunk -> embed -> persist.

Deliberately separated from `vector_store.py`'s query path (Section 6 of
Phase 1): this module is only ever invoked by `scripts/run_ingest.py`, never
by the request-serving path, so a request never pays the cost of
re-embedding the source document.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.retrieval.loader import load_and_chunk_source_document
from app.retrieval.vector_store import VectorStoreClient

logger = logging.getLogger(__name__)


def run_ingestion(source_path: Path | None = None) -> None:
    """Build and persist the FAISS index from the configured source document."""
    logger.info("Loading and chunking source document...")
    chunks = load_and_chunk_source_document(source_path)
    logger.info("Produced %d chunks.", len(chunks))

    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx

    client = VectorStoreClient()
    logger.info("Embedding chunks and building FAISS index...")
    client.build_from_documents(chunks)
    logger.info("Vector store persisted to %s", client.store_dir)