"""
Document loading and chunking.

Isolated from both the embedding step and the vector store so each concern
(load, split, embed, persist) can be tested and swapped independently
(SOLID: SRP/OCP — new document formats can be added by extending
`_select_loader` without modifying callers).
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from app.config import settings


class UnsupportedDocumentTypeError(ValueError):
    """Raised when the source document's extension has no registered loader."""


def _select_loader(path: Path):
    """Return the appropriate LangChain document loader for `path`'s suffix."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path))
    if suffix in (".txt",):
        return TextLoader(str(path), encoding="utf-8")
    if suffix in (".md", ".markdown"):
        return UnstructuredMarkdownLoader(str(path))
    raise UnsupportedDocumentTypeError(
        f"No loader registered for file type '{suffix}' (path: {path})"
    )


def load_source_document(path: Path | None = None) -> list[Document]:
    """Load the raw source document into LangChain `Document` objects."""
    document_path = path or settings.source_document_path
    if not document_path.exists():
        raise FileNotFoundError(f"Source document not found at {document_path}")

    loader = _select_loader(document_path)
    return loader.load()


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split loaded documents into overlapping chunks sized for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_chunk_source_document(path: Path | None = None) -> list[Document]:
    """Convenience pipeline: load the source document and chunk it."""
    documents = load_source_document(path)
    return chunk_documents(documents)