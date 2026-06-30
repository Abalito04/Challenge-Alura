import json
from pathlib import Path

from app.rag.chunking import split_documents
from app.rag.documents import load_pdf_corpus
from app.rag.evaluation import evaluate_source_recall
from app.rag.vectorstore import index_documents, open_vectorstore
from tests.fakes import HashingEmbeddings


def test_offline_chroma_retrieves_relevant_sources(tmp_path: Path) -> None:
    pages = load_pdf_corpus(Path("source_documents"))
    chunks = split_documents(pages, chunk_size=900, chunk_overlap=150)
    store = open_vectorstore(
        embeddings=HashingEmbeddings(),
        persist_dir=tmp_path / "chroma",
        collection_name="medinova_test",
    )
    assert index_documents(store, chunks) == len(chunks)

    cases = [
        ("¿Cuánto antes debo cancelar un turno?", "politica_cancelaciones_reagendamiento.pdf"),
        ("¿Qué planes acepta Salud Federal?", "guia_convenios_coberturas.pdf"),
        ("¿Quién puede acceder a mis datos?", "politica_privacidad_pacientes.pdf"),
        ("¿Administración interpreta resultados?", "instrucciones_pre_post_consulta.pdf"),
    ]
    for question, expected_source in cases:
        results = store.similarity_search(question, k=5)
        assert expected_source in {doc.metadata["source"] for doc in results}


def test_golden_dataset_offline_source_recall(tmp_path: Path) -> None:
    pages = load_pdf_corpus(Path("source_documents"))
    chunks = split_documents(pages, chunk_size=900, chunk_overlap=150)
    store = open_vectorstore(
        embeddings=HashingEmbeddings(),
        persist_dir=tmp_path / "golden_chroma",
        collection_name="medinova_golden_test",
    )
    index_documents(store, chunks)
    cases = json.loads(Path("tests/data/golden_questions.json").read_text(encoding="utf-8"))
    evaluation = evaluate_source_recall(store, cases, k=5)
    assert evaluation.evaluated == 14
    assert evaluation.source_recall_at_k >= 0.70, evaluation
