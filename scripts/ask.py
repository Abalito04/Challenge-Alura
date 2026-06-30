import argparse

from app.agent.graph import build_agent_graph
from app.config import get_settings
from app.llm_provider import create_chat_model
from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import open_vectorstore


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask Medinova AI Agent from the terminal")
    parser.add_argument("question")
    args = parser.parse_args()

    settings = get_settings()
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
    llm = create_chat_model(
        provider=settings.llm_provider,
        model=settings.llm_model,
        api_key=settings.api_key_for(settings.llm_provider),
        fallback_provider=settings.llm_fallback_provider,
        fallback_model=settings.llm_fallback_model,
        fallback_api_key=(
            settings.api_key_for(settings.llm_fallback_provider)
            if settings.llm_fallback_provider
            else None
        ),
    )
    graph = build_agent_graph(
        vectorstore=store,
        llm=llm,
        retrieval_k=settings.retrieval_k,
        score_threshold=settings.retrieval_score_threshold,
    )
    result = graph.invoke({"question": args.question})
    print(result["answer"])
    if result.get("citations"):
        print("\nFuentes:")
        for citation in result["citations"]:
            print(f"- {citation['source']}, página {citation['page']}")


if __name__ == "__main__":
    main()
