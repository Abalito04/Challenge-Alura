import json
import argparse
from pathlib import Path

from app.config import get_settings
from app.rag.embeddings import create_embeddings
from app.rag.evaluation import evaluate_source_recall
from app.rag.vectorstore import open_vectorstore


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate source recall of the persisted index")
    parser.add_argument("--k", type=int, default=None)
    args = parser.parse_args()
    settings = get_settings()
    retrieval_k = args.k or settings.retrieval_k
    embeddings = create_embeddings(
        provider=settings.embeddings_provider,
        model=settings.embeddings_model,
        api_key=settings.api_key_for(settings.embeddings_provider),
    )
    store = open_vectorstore(
        embeddings=embeddings,
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.vector_collection_name,
    )
    cases = json.loads(
        Path("tests/data/golden_questions.json").read_text(encoding="utf-8")
    )
    result = evaluate_source_recall(store, cases, k=retrieval_k)
    print(
        f"Source Recall@{retrieval_k}: "
        f"{result.hits}/{result.evaluated} ({result.source_recall_at_k:.1%})"
    )
    print("Misses:", ", ".join(result.misses) if result.misses else "none")


if __name__ == "__main__":
    main()
