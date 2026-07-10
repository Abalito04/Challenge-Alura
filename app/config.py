from functools import lru_cache
from pathlib import Path
import re

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.5-flash"
    llm_fallback_provider: str | None = "gemini"
    llm_fallback_model: str = "gemini-2.5-flash"
    embeddings_provider: str = "gemini"
    embeddings_model: str = "gemini-embedding-001"
    gemini_api_key: str | None = Field(
        default=None,
        repr=False,
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    )
    openai_api_key: str | None = Field(default=None, repr=False)
    cohere_api_key: str | None = Field(default=None, repr=False)
    document_upload_password: str | None = Field(default=None, repr=False)

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
        supported = {"gemini", "openai", "cohere"}
        for field_name, provider in (
            ("LLM_PROVIDER", self.llm_provider),
            ("EMBEDDINGS_PROVIDER", self.embeddings_provider),
        ):
            if provider.lower() not in supported:
                raise ValueError(f"Unsupported {field_name}: {provider}")
        if self.llm_fallback_provider and self.llm_fallback_provider.lower() not in supported:
            raise ValueError(
                f"Unsupported LLM_FALLBACK_PROVIDER: {self.llm_fallback_provider}"
            )
        if not 0.0 <= self.retrieval_score_threshold <= 1.0:
            raise ValueError("RETRIEVAL_SCORE_THRESHOLD must be between 0 and 1")

    def api_key_for(self, provider: str) -> str | None:
        keys = {
            "gemini": self.gemini_api_key,
            "openai": self.openai_api_key,
            "cohere": self.cohere_api_key,
        }
        try:
            return keys[provider.lower()]
        except KeyError as exc:
            raise ValueError(f"Unsupported provider: {provider}") from exc

    @property
    def vector_collection_name(self) -> str:
        if (
            self.embeddings_provider.lower() == "gemini"
            and self.embeddings_model.lower() == "gemini-embedding-001"
        ):
            return self.chroma_collection
        identity = f"{self.embeddings_provider}_{self.embeddings_model}".lower()
        slug = re.sub(r"[^a-z0-9]+", "_", identity).strip("_")
        return f"{self.chroma_collection}_{slug}"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_rag_configuration()
    return settings
