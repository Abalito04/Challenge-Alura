from app.config import get_settings
from app.rag.pipeline import ingest_corpus


def main() -> None:
    result = ingest_corpus(get_settings())
    print(
        "Ingestion completed: "
        f"{result.files} files, {result.pages} pages, {result.chunks} chunks, "
        f"collection={result.collection_name}"
    )


if __name__ == "__main__":
    main()

