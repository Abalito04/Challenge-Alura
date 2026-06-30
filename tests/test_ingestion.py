from pathlib import Path

from app.config import Settings
from app.rag.chunking import split_documents
from app.rag.documents import load_pdf_corpus
from app.rag.pipeline import ingest_corpus
from tests.fakes import HashingEmbeddings


def test_loads_complete_pdf_corpus() -> None:
    pages = load_pdf_corpus(Path("source_documents"))
    assert len(pages) == 25
    assert len({page.metadata["source"] for page in pages}) == 5
    assert all(page.metadata["page"] >= 1 for page in pages)
    assert all(len(page.metadata["source_sha256"]) == 64 for page in pages)
    assert all(page.metadata["corpus"] == "medinova-v2" for page in pages)


def test_chunking_preserves_traceability() -> None:
    pages = load_pdf_corpus(Path("source_documents"))
    chunks = split_documents(pages, chunk_size=900, chunk_overlap=150)
    assert len(chunks) > len(pages)
    assert len({chunk.metadata["chunk_id"] for chunk in chunks}) == len(chunks)
    assert all(chunk.metadata.get("source") for chunk in chunks)
    assert all(chunk.metadata.get("page") for chunk in chunks)
    assert all(len(chunk.page_content) <= 900 for chunk in chunks)


def test_complete_offline_ingestion_pipeline(tmp_path: Path) -> None:
    settings = Settings(
        source_documents_dir=Path("source_documents"),
        chroma_persist_dir=tmp_path / "chroma",
        chroma_collection="medinova_pipeline_test",
    )
    result = ingest_corpus(settings, embeddings=HashingEmbeddings())
    assert result.files == 5
    assert result.pages == 25
    assert result.chunks > 25
