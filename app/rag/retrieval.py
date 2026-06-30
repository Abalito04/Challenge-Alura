from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from langchain_core.documents import Document


class ScoredVectorStore(Protocol):
    def similarity_search_with_relevance_scores(
        self, query: str, *, k: int
    ) -> list[tuple[Document, float]]: ...


@dataclass(frozen=True)
class RetrievalResult:
    documents: tuple[Document, ...]
    scores: tuple[float, ...]
    sufficient: bool


def retrieve_context(
    store: ScoredVectorStore,
    question: str,
    *,
    k: int,
    score_threshold: float,
) -> RetrievalResult:
    scored = store.similarity_search_with_relevance_scores(question, k=k)
    accepted = [(doc, score) for doc, score in scored if score >= score_threshold]
    return RetrievalResult(
        documents=tuple(doc for doc, _ in accepted),
        scores=tuple(float(score) for _, score in accepted),
        sufficient=bool(accepted),
    )

