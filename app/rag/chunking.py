from __future__ import annotations

import hashlib
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def _normalize(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_documents(
    documents: list[Document], *, chunk_size: int = 900, chunk_overlap: int = 150
) -> list[Document]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = [
        Document(page_content=_normalize(doc.page_content), metadata=dict(doc.metadata))
        for doc in documents
        if _normalize(doc.page_content)
    ]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        keep_separator=True,
        add_start_index=True,
    )
    chunks = splitter.split_documents(normalized)
    for chunk_index, chunk in enumerate(chunks):
        identity = "|".join(
            [
                str(chunk.metadata.get("source_sha256", "")),
                str(chunk.metadata.get("page", "")),
                str(chunk.metadata.get("start_index", "")),
                chunk.page_content,
            ]
        )
        chunk.metadata["chunk_id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        chunk.metadata["chunk_index"] = chunk_index
    return chunks

