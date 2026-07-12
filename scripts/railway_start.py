from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.config import get_settings
from app.rag.pipeline import ingest_corpus


def _collection_has_documents() -> bool:
    settings = get_settings()
    if not settings.chroma_persist_dir.exists():
        return False

    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        collection = client.get_collection(settings.vector_collection_name)
        return collection.count() > 0
    except Exception:
        return False


def _prepare_runtime_data() -> None:
    settings = get_settings()
    Path("data").mkdir(parents=True, exist_ok=True)
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    if os.getenv("SKIP_STARTUP_INGEST", "").lower() in {"1", "true", "yes"}:
        print("Startup ingest skipped by SKIP_STARTUP_INGEST.")
        return

    if _collection_has_documents():
        print(
            "Existing Chroma collection found: "
            f"{settings.vector_collection_name}. Startup ingest skipped."
        )
        return

    print("No persisted Chroma collection found. Running startup ingest...")
    result = ingest_corpus(settings)
    print(
        "Startup ingest completed: "
        f"{result.files} files, {result.pages} pages, {result.chunks} chunks, "
        f"collection={result.collection_name}"
    )


def main() -> None:
    port = os.getenv("PORT", "8501")

    try:
        _prepare_runtime_data()
    except Exception as exc:
        print(
            "WARNING: Startup ingest could not be completed. "
            "The app will still start, but documental RAG may fail until "
            f"configuration is fixed. Detail: {exc}",
            file=sys.stderr,
        )

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.address=0.0.0.0",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
