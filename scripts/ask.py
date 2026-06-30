import argparse

from app.agent.graph import build_agent_graph
from app.config import get_settings
from app.llm_provider import create_gemini_chat_model
from app.rag.embeddings import create_gemini_embeddings
from app.rag.vectorstore import open_vectorstore


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask Medinova AI Agent from the terminal")
    parser.add_argument("question")
    args = parser.parse_args()

    settings = get_settings()
    embeddings = create_gemini_embeddings(
        model=settings.embeddings_model, api_key=settings.gemini_api_key
    )
    store = open_vectorstore(
        embeddings=embeddings,
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection,
    )
    llm = create_gemini_chat_model(
        model=settings.llm_model,
        fallback_model=settings.llm_fallback_model,
        api_key=settings.gemini_api_key,
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
