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
        embeddings_provider="cohere",
        embeddings_model="embed-v4.0",
        cohere_api_key="cohere-test-secret",
    )
    assert settings.api_key_for("cohere") == "cohere-test-secret"
    assert settings.vector_collection_name.endswith("cohere_embed_v4_0")


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
