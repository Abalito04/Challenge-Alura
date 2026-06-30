from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class CorpusError(RuntimeError):
    """Raised when the configured source corpus cannot be ingested safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_pdf_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise CorpusError(f"Source directory does not exist: {source_dir}")
    files = sorted(path for path in source_dir.glob("*.pdf") if path.is_file())
    if not files:
        raise CorpusError(f"No PDF files found in: {source_dir}")
    return files


def load_pdf_corpus(source_dir: Path) -> list[Document]:
    """Load every PDF as page-level LangChain documents with stable metadata."""

    documents: list[Document] = []
    for path in discover_pdf_files(source_dir):
        file_hash = _sha256(path)
        try:
            pages = PyPDFLoader(str(path), mode="page").load()
        except Exception as exc:  # loader errors vary by pypdf version
            raise CorpusError(f"Could not read PDF {path.name}: {exc}") from exc

        if not pages or not any(page.page_content.strip() for page in pages):
            raise CorpusError(f"PDF has no extractable text: {path.name}")

        for page_index, page in enumerate(pages):
            if not page.page_content.strip():
                continue
            page.metadata.update(
                {
                    "source": path.name,
                    "source_path": path.as_posix(),
                    "source_sha256": file_hash,
                    "page": page_index + 1,
                    "corpus": "medinova-v2",
                }
            )
            documents.append(page)
    return documents

