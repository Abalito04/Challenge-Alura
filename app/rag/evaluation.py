from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalEvaluation:
    evaluated: int
    hits: int
    source_recall_at_k: float
    misses: tuple[str, ...]


def evaluate_source_recall(vectorstore: Any, cases: list[dict], *, k: int = 5) -> RetrievalEvaluation:
    """Measure whether at least one expected source appears in the top-k results."""

    evaluated = 0
    hits = 0
    misses: list[str] = []
    for case in cases:
        expected = set(case.get("sources", []))
        if not expected or case.get("route"):
            continue
        evaluated += 1
        results = vectorstore.similarity_search(case["question"], k=k)
        retrieved = {doc.metadata.get("source") for doc in results}
        if expected.intersection(retrieved):
            hits += 1
        else:
            misses.append(case["id"])
    score = hits / evaluated if evaluated else 0.0
    return RetrievalEvaluation(evaluated, hits, score, tuple(misses))

