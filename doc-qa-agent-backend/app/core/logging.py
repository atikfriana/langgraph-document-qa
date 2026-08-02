"""
Structured logging configuration.

Emits JSON log lines in production (machine-parseable, ready for log
aggregation) and human-readable lines in local development, switched purely
by config — application code never formats logs itself, it just calls
`logging.getLogger(__name__)` as usual.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

_RESERVED_LOG_RECORD_ATTRS = frozenset(
    logging.LogRecord(
        name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
    ).__dict__.keys()
)


class JsonFormatter(logging.Formatter):
    """Renders each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Include any extra fields passed via `logger.info(..., extra={...})`.
        for key, value in record.__dict__.items():
            if key not in _RESERVED_LOG_RECORD_ATTRS and key not in payload:
                payload[key] = value

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure the root logger once, at process startup."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    # Avoid duplicate handlers if called more than once (e.g. under reload).
    root_logger.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)

    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers unless explicitly debugging.
    for noisy_logger in ("httpx", "httpcore", "urllib3", "openai._base_client"):
        logging.getLogger(noisy_logger).setLevel(
            logging.DEBUG if settings.debug else logging.WARNING
        )


def get_logger(name: str) -> logging.Logger:
    """Convenience accessor mirroring `logging.getLogger`, for consistency."""
    return logging.getLogger(name)