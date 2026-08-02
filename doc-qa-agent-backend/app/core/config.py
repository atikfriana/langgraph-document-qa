"""
Application-wide configuration (infrastructure layer).

This is the single source of settings for the entire application — the only
`Settings` definition anywhere in the codebase. `app/config.py` is now a
thin backward-compatible re-export shim (`from app.core.config import *`)
for any module still importing `app.config`, rather than a second
definition. Every environment-dependent value lives in exactly one place
here, so a config change never requires touching business logic or risks
drifting between two independently maintained classes.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App metadata ---
    app_name: str = Field(default="doc-qa-agent", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # --- API / server ---
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["*"], alias="CORS_ALLOW_ORIGINS"
    )

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    # --- Google Gemini ---
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    chat_model_name: str = Field(default="gemini-3-flash-preview", alias="CHAT_MODEL_NAME")
    embedding_model_name: str = Field(
        default="models/gemini-embedding-001", alias="EMBEDDING_MODEL_NAME"
    )
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")

    # --- Web search tool ---
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    # --- Retrieval ---
    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    source_document_path: Path = Field(
        default=Path("data/sample_document.pdf"), alias="SOURCE_DOCUMENT_PATH"
    )
    vector_store_dir: Path = Field(
        default=Path("vector_db"), alias="VECTOR_STORE_DIR"
    )
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=4, alias="RETRIEVAL_TOP_K")
    retrieval_score_threshold: float = Field(
        default=0.25, alias="RETRIEVAL_SCORE_THRESHOLD"
    )

    # --- Memory ---
    checkpointer_backend: str = Field(default="memory", alias="CHECKPOINTER_BACKEND")
    sqlite_checkpoint_path: Path = Field(
        default=Path("vector_db/checkpoints.sqlite"), alias="SQLITE_CHECKPOINT_PATH"
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide cached Settings instance (avoids re-parsing env)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()