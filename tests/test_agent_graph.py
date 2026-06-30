from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agent.classification import classify_intent
from app.agent.graph import build_agent_graph


class StubVectorStore:
    def similarity_search_with_relevance_scores(self, query: str, *, k: int):
        if "feriado" in query.lower():
            return []
        return [
            (
                Document(
                    page_content="Las cancelaciones se informan con 24 horas de anticipación.",
                    metadata={"source": "politica_cancelaciones_reagendamiento.pdf", "page": 1},
                ),
                0.9,
            )
        ]


def graph():
    return build_agent_graph(
        vectorstore=StubVectorStore(),
        llm=FakeListChatModel(responses=["Debés avisar con 24 horas de anticipación."]),
    )


def test_intent_classifier_keeps_admin_questions_documental() -> None:
    assert classify_intent("¿Cómo cancelo un turno?") == "documental"
    assert classify_intent("¿Qué medicamento tomo?") == "clinical"
    assert classify_intent("Quiero solicitar un turno") == "appointment"
    assert classify_intent("¿Podemos gestionar un turno?") == "appointment"
    assert classify_intent("¿Cómo puedo pedir un turno?") == "appointment"
    assert classify_intent("¿Cómo cancelo un turno?") == "documental"
    assert classify_intent("Hola") == "greeting"
    assert classify_intent("Muchas gracias!") == "greeting"
    assert classify_intent("Hola, ¿qué cardiólogos atienden?") == "documental"


def test_graph_generates_grounded_answer_with_citation() -> None:
    result = graph().invoke({"question": "¿Cuánto antes debo cancelar?"})
    assert "24 horas" in result["answer"]
    assert result["citations"][0]["source"] == "politica_cancelaciones_reagendamiento.pdf"


def test_graph_rejects_clinical_question_without_sources() -> None:
    result = graph().invoke({"question": "¿Qué medicamento tomo para la fiebre?"})
    assert "No puedo brindar diagnósticos" in result["answer"]
    assert result["citations"] == ()


def test_graph_abstains_without_context() -> None:
    result = graph().invoke({"question": "¿Atienden todos los feriados?"})
    assert "información suficiente" in result["answer"]


def test_graph_answers_greeting_without_retrieval_or_model() -> None:
    result = graph().invoke({"question": "Hola"})
    assert "¡Hola!" in result["answer"]
    assert "¿Qué necesitás consultar?" in result["answer"]
    assert result["citations"] == ()
    assert result.get("documents") is None


def test_graph_routes_appointment_request_without_rag() -> None:
    result = graph().invoke({"question": "¿Podemos gestionar un turno?"})
    assert "sección Solicitudes" in result["answer"]
    assert "pendiente" in result["answer"]
    assert result["citations"] == ()
    assert result.get("documents") is None


def test_follow_up_question_is_contextualized_for_retrieval() -> None:
    result = graph().invoke(
        {
            "question": "¿Y sus horarios?",
            "conversation": (
                {"role": "user", "content": "¿Qué cardiólogos atienden?"},
                {"role": "assistant", "content": "Atienden dos especialistas."},
            ),
        }
    )
    assert "¿Qué cardiólogos atienden?" in result["retrieval_question"]
    assert "¿Y sus horarios?" in result["retrieval_question"]


def test_short_confirmation_uses_appointment_history() -> None:
    result = graph().invoke(
        {
            "question": "Dale",
            "conversation": (
                {
                    "role": "assistant",
                    "content": "¿Querés registrar una solicitud de turno?",
                },
            ),
        }
    )
    assert result["intent"] == "appointment"
    assert "sección Solicitudes" in result["answer"]
    assert result.get("documents") is None
