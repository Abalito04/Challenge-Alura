from __future__ import annotations

from langchain_core.runnables import Runnable


def create_gemini_chat_model(
    *, model: str, api_key: str | None, fallback_model: str | None = None
) -> Runnable:
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is required. Use .env locally or OCI Vault in deployment."
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    primary = ChatGoogleGenerativeAI(
        model=model,
        api_key=api_key,
        temperature=0,
        max_retries=1,
    )
    if not fallback_model or fallback_model == model:
        return primary
    fallback = ChatGoogleGenerativeAI(
        model=fallback_model,
        api_key=api_key,
        temperature=0,
        max_retries=1,
    )
    return primary.with_fallbacks([fallback])
