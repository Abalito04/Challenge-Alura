import pytest

from app.config import Settings
from app.llm_provider import create_gemini_chat_model
from app.rag.embeddings import create_gemini_embeddings


def test_rejects_overlap_equal_to_chunk_size() -> None:
    settings = Settings(chunk_size=500, chunk_overlap=500)
    with pytest.raises(ValueError, match="smaller"):
        settings.validate_rag_configuration()


def test_secret_is_not_required_for_offline_configuration() -> None:
    settings = Settings(
        gemini_api_key=None,
        openai_api_key="openai-test-secret",
        cohere_api_key="cohere-test-secret",
    )
    assert settings.gemini_api_key is None
    representation = repr(settings)
    assert "openai-test-secret" not in representation
    assert "cohere-test-secret" not in representation


def test_provider_keys_and_vector_collections_are_resolved_independently() -> None:
    settings = Settings(
        embeddings_provider="openai",
        embeddings_model="text-embedding-3-small",
        openai_api_key="openai-test-secret",
    )
    assert settings.api_key_for("openai") == "openai-test-secret"
    assert settings.vector_collection_name.endswith("openai_text_embedding_3_small")


def test_cohere_is_the_default_provider(monkeypatch) -> None:
    for name in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_FALLBACK_PROVIDER",
        "LLM_FALLBACK_MODEL",
        "EMBEDDINGS_PROVIDER",
        "EMBEDDINGS_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "cohere"
    assert settings.llm_model == "command-a-03-2025"
    assert settings.llm_fallback_provider == "gemini"
    assert settings.llm_fallback_model == "gemini-2.5-flash"
    assert settings.embeddings_provider == "cohere"
    assert settings.embeddings_model == "embed-v4.0"
    assert settings.vector_collection_name == "medinova_documents"


def test_google_api_key_is_accepted_as_gemini_alias(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-alias-test-secret")
    settings = Settings(_env_file=None)
    assert settings.api_key_for("gemini") == "google-alias-test-secret"


def test_gemini_embeddings_factory_matches_installed_integration() -> None:
    embeddings = create_gemini_embeddings(
        model="gemini-embedding-001",
        api_key="test-key-never-sent",
    )
    assert embeddings.model == "gemini-embedding-001"


def test_chat_factory_configures_fallback_without_network_call() -> None:
    model = create_gemini_chat_model(
        model="gemini-3.5-flash",
        fallback_model="gemini-2.5-flash",
        api_key="test-key-never-sent",
    )
    assert len(model.fallbacks) == 1
