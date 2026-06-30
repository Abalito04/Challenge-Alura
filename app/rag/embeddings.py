from __future__ import annotations

from langchain_core.embeddings import Embeddings


def create_embeddings(*, provider: str, model: str, api_key: str | None) -> Embeddings:
    provider = provider.lower()
    if not api_key:
        raise ValueError(
            f"{provider.upper()}_API_KEY is required for real indexing. "
            "Use .env locally or OCI Vault in deployment."
        )
    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(model=model, api_key=api_key)
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=model, api_key=api_key)
    if provider == "cohere":
        from langchain_cohere import CohereEmbeddings

        return CohereEmbeddings(model=model, cohere_api_key=api_key)
    raise ValueError(f"Unsupported embeddings provider: {provider}")


def create_gemini_embeddings(*, model: str, api_key: str | None) -> Embeddings:
    """Backward-compatible Gemini shortcut."""
    return create_embeddings(provider="gemini", model=model, api_key=api_key)
