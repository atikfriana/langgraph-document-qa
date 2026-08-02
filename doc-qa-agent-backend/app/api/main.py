"""
FastAPI application entrypoint.

Wires together lifespan startup/shutdown, middleware, CORS, exception
handling, and route registration. This is the composition root: the one
place allowed to know about every concrete module, so it can construct and
inject them into `app.state` for the rest of the app to consume via DI.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.graph.builder import build_agent_graph
from app.retrieval.vector_store import get_vector_store_client, VectorStoreNotBuiltError

configure_logging()
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs each request's method, path, status, latency, and a request id."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = str(uuid.uuid4())
        started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build expensive singletons once at startup; release them at shutdown.

    Uses `get_vector_store_client()` — the same module-level accessor used
    by `app.graph.nodes.retrieve` — rather than constructing a separate
    `VectorStoreClient()` instance here. This guarantees the API layer's
    readiness check (`/health/ready`) and the graph's retrieval node are
    always backed by the exact same loaded FAISS index in memory, not two
    independent copies.
    """
    logger.info("Starting up: loading vector store...")
    try:
        vector_store_client = get_vector_store_client()
        logger.info("Vector store loaded successfully.")
    except VectorStoreNotBuiltError:
        vector_store_client = None
        logger.warning(
            "Vector store not found on disk. /chat will fail until ingestion "
            "is run (see scripts/run_ingest.py)."
        )

    logger.info("Compiling LangGraph agent...")
    app.state.vector_store_client = vector_store_client
    app.state.agent_graph = build_agent_graph()
    logger.info("Startup complete.")

    yield

    logger.info("Shutting down.")


def create_app() -> FastAPI:
    """Application factory — constructs and fully configures the FastAPI app."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(chat_router)

    return app


app = create_app()