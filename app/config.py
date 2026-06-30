from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.5-flash"
    llm_fallback_model: str = "gemini-2.5-flash"
    embeddings_provider: str = "gemini"
    embeddings_model: str = "gemini-embedding-001"
    gemini_api_key: str | None = Field(default=None, repr=False)

    source_documents_dir: Path = Path("source_documents")
    chroma_persist_dir: Path = Path("data/chroma")
    chroma_collection: str = "medinova_documents"
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_k: int = 3
    retrieval_score_threshold: float = 0.25

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value < 200:
            raise ValueError("CHUNK_SIZE must be at least 200 characters")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int) -> int:
        if value < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative")
        return value

    def validate_rag_configuration(self) -> None:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        if self.embeddings_provider != "gemini":
            raise ValueError(f"Unsupported embeddings provider: {self.embeddings_provider}")
        if not 0.0 <= self.retrieval_score_threshold <= 1.0:
            raise ValueError("RETRIEVAL_SCORE_THRESHOLD must be between 0 and 1")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_rag_configuration()
    return settings
