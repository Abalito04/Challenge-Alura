from __future__ import annotations

from dataclasses import dataclass

from langchain_core.embeddings import Embeddings

from app.config import Settings
from app.rag.chunking import split_documents
from app.rag.documents import load_pdf_corpus
from app.rag.embeddings import create_gemini_embeddings
from app.rag.vectorstore import index_documents, open_vectorstore


@dataclass(frozen=True)
class IngestionResult:
    files: int
    pages: int
    chunks: int
    collection_name: str


def ingest_corpus(settings: Settings, *, embeddings: Embeddings | None = None) -> IngestionResult:
    settings.validate_rag_configuration()
    pages = load_pdf_corpus(settings.source_documents_dir)
    chunks = split_documents(
        pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    embedding_model = embeddings or create_gemini_embeddings(
        model=settings.embeddings_model,
        api_key=settings.gemini_api_key,
    )
    store = open_vectorstore(
        embeddings=embedding_model,
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection,
    )
    indexed = index_documents(store, chunks)
    return IngestionResult(
        files=len({page.metadata["source"] for page in pages}),
        pages=len(pages),
        chunks=indexed,
        collection_name=settings.chroma_collection,
    )

