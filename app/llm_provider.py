from __future__ import annotations

from langchain_core.runnables import Runnable


def _create_chat_model(*, provider: str, model: str, api_key: str | None) -> Runnable:
    provider = provider.lower()
    if not api_key:
        raise ValueError(
            f"{provider.upper()}_API_KEY is required. Use .env locally or OCI Vault in deployment."
        )
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model, api_key=api_key, temperature=0, max_retries=1
        )
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key, temperature=0, max_retries=1)
    if provider == "cohere":
        from langchain_cohere import ChatCohere

        return ChatCohere(model=model, cohere_api_key=api_key, temperature=0)
    raise ValueError(f"Unsupported chat provider: {provider}")


def create_chat_model(
    *,
    provider: str,
    model: str,
    api_key: str | None,
    fallback_provider: str | None = None,
    fallback_model: str | None = None,
    fallback_api_key: str | None = None,
) -> Runnable:
    primary = _create_chat_model(provider=provider, model=model, api_key=api_key)
    if not fallback_model:
        return primary
    resolved_fallback_provider = fallback_provider or provider
    if resolved_fallback_provider == provider and fallback_model == model:
        return primary
    fallback = _create_chat_model(
        provider=resolved_fallback_provider,
        model=fallback_model,
        api_key=(
            fallback_api_key
            if resolved_fallback_provider.lower() != provider.lower()
            else fallback_api_key or api_key
        ),
    )
    return primary.with_fallbacks([fallback])


def create_gemini_chat_model(
    *, model: str, api_key: str | None, fallback_model: str | None = None
) -> Runnable:
    """Backward-compatible Gemini shortcut."""
    return create_chat_model(
        provider="gemini",
        model=model,
        api_key=api_key,
        fallback_provider="gemini",
        fallback_model=fallback_model,
    )
