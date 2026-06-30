import pytest

from app.config import Settings
from app.llm_provider import create_gemini_chat_model
from app.rag.embeddings import create_gemini_embeddings


def test_rejects_overlap_equal_to_chunk_size() -> None:
    settings = Settings(chunk_size=500, chunk_overlap=500)
    with pytest.raises(ValueError, match="smaller"):
        settings.validate_rag_configuration()


def test_secret_is_not_required_for_offline_configuration() -> None:
    settings = Settings(gemini_api_key=None)
    assert settings.gemini_api_key is None
    assert "api_key" not in repr(settings).lower()


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
