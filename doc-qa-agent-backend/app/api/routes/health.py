"""
Health and readiness check endpoint.

Distinguishes "process is up" from "process can actually serve traffic"
(vector store loaded, API key present) — the latter is what orchestrators
(Kubernetes, Docker Compose) should gate readiness/traffic-routing on.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_vector_store_client
from app.core.config import settings
from app.retrieval.vector_store import VectorStoreClient

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Liveness/readiness payload."""

    status: str
    environment: str
    vector_store_ready: bool


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Lightweight liveness check — never fails, used by load balancers."""
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        vector_store_ready=False,
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(
    vector_store: Annotated[VectorStoreClient, Depends(get_vector_store_client)],
) -> HealthResponse:
    """Readiness check — fails (503, via VectorStoreUnavailableError) until
    the retrieval index is actually loaded and the service can serve /chat."""
    return HealthResponse(
        status="ready",
        environment=settings.environment,
        vector_store_ready=vector_store.is_loaded,
    )