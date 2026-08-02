"""
CLI entrypoint to (re)build the FAISS vector index from the source document.

Run from the project root before serving the API for the first time, or
whenever `data/sample_document.pdf` changes:

    python scripts/run_ingest.py

This is also what `docker-compose.yml`'s `ingest` service invokes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure the project root is importable when this script is invoked directly
# (e.g. `python scripts/run_ingest.py` from the repo root), since Python only
# adds the script's own directory to sys.path by default, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval.ingest import run_ingestion  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    run_ingestion()


if __name__ == "__main__":
    main()