from __future__ import annotations

from langchain_core.embeddings import Embeddings


def create_gemini_embeddings(*, model: str, api_key: str | None) -> Embeddings:
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is required for real indexing. "
            "Use .env locally or OCI Vault in deployment."
        )
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(model=model, api_key=api_key)
