from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def open_vectorstore(
    *, embeddings: Embeddings, persist_dir: Path, collection_name: str
) -> Chroma:
    persist_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
        collection_metadata={"hnsw:space": "cosine"},
    )


def index_documents(vectorstore: Chroma, documents: list[Document]) -> int:
    if not documents:
        raise ValueError("Cannot index an empty document list")
    ids = [str(doc.metadata["chunk_id"]) for doc in documents]
    vectorstore.add_documents(documents=documents, ids=ids)
    return len(ids)

