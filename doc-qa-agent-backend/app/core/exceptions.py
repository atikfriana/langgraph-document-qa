"""
Custom exception hierarchy and FastAPI exception handlers.

Domain/infrastructure code raises specific, typed exceptions (never bare
`Exception`); this module is the only place that knows how to translate them
into HTTP responses. This keeps error-handling policy (status codes, response
shape) out of route handlers entirely (SRP), and means adding a new
exception type never requires touching every route that might raise it.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base class for all application-raised errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class SessionNotFoundError(AgentError):
    """Raised when a requested session/thread has no recorded history."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "session_not_found"


class InvalidRequestError(AgentError):
    """Raised for well-formed-but-semantically-invalid client input."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "invalid_request"


class GraphExecutionError(AgentError):
    """Raised when the LangGraph agent fails to complete a turn."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "graph_execution_failed"


class VectorStoreUnavailableError(AgentError):
    """Raised when the retrieval index is not built/loaded."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "vector_store_unavailable"


def _error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": error_code, "message": message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the FastAPI app instance."""

    @app.exception_handler(AgentError)
    async def handle_agent_error(request: Request, exc: AgentError) -> JSONResponse:
        logger.warning(
            "Handled application error",
            extra={
                "error_code": exc.error_code,
                "path": request.url.path,
                "details": exc.details,
            },
        )
        return _error_response(exc.status_code, exc.error_code, exc.message)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception", extra={"path": request.url.path}
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected error occurred. Please try again.",
        )