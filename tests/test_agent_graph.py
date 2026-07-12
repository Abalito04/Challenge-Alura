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
    assert classify_intent("ver turnos") == "appointment"
    assert classify_intent("turnos con gastroenterologo?") == "appointment"
    assert classify_intent("boca vs river") == "invalid"
    assert classify_intent("que especialidades hay") == "directory"
    assert classify_intent("que medicos hay") == "directory"
    assert classify_intent("que medicos hay disponibles") == "directory"
    assert classify_intent("¿Cómo cancelo un turno?") == "documental"
    assert classify_intent("Hola") == "greeting"
    assert classify_intent("hola buenas tardes") == "greeting"
    assert classify_intent("hola buenos dias") == "greeting"
    assert classify_intent("buenos días") == "greeting"
    assert classify_intent("buenas noches!") == "greeting"
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


def test_graph_answers_compound_greeting_without_retrieval_or_model() -> None:
    result = graph().invoke({"question": "hola buenas tardes"})
    assert "¡Hola!" in result["answer"]
    assert result["citations"] == ()
    assert result.get("documents") is None


def test_graph_answers_plural_morning_greeting_without_retrieval_or_model() -> None:
    result = graph().invoke({"question": "hola buenos dias"})
    assert "¡Hola!" in result["answer"]
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


def test_appointment_derivation_preserves_professional_and_specialty() -> None:
    result = graph().invoke(
        {
            "question": "Bien, quiero un turno con la dra",
            "conversation": (
                {"role": "user", "content": "¿Qué cardiólogos atienden?"},
                {
                    "role": "assistant",
                    "content": "Dr. Andrés Ferreyra y Dra. Emilia Ríos atienden en Cardiología.",
                },
            ),
        }
    )
    assert result["intent"] == "appointment"
    assert result["appointment_professional"] == "Dra. Emilia Ríos"
    assert result["appointment_specialty"] == "Cardiología"
    assert "Dra. Emilia Ríos" in result["answer"]


def test_appointment_derivation_detects_requested_specialty() -> None:
    result = graph().invoke({"question": "turnos con gastroenterologo?"})
    assert result["intent"] == "appointment"
    assert result["appointment_specialty"] == "Gastroenterología"
    assert "Gastroenterología" in result["answer"]


def test_directory_question_answers_without_model() -> None:
    result = graph().invoke({"question": "que especialidades hay"})
    assert result["intent"] == "directory"
    assert "Cardiología" in result["answer"]
    assert "Gastroenterología" in result["answer"]
    assert result["citations"][0]["source"] == "directorio_especialistas_y_servicios.pdf"
    assert result.get("documents") is None


def test_directory_professionals_question_answers_without_model() -> None:
    result = graph().invoke({"question": "que medicos hay disponibles"})
    assert result["intent"] == "directory"
    assert "profesionales por especialidad" in result["answer"]
    assert "no confirma disponibilidad de turnos" in result["answer"]
    assert result.get("documents") is None


def test_directory_professionals_short_question_answers_without_model() -> None:
    result = graph().invoke({"question": "que medicos hay"})
    assert result["intent"] == "directory"
    assert "Dr. Andrés Ferreyra" in result["answer"]
    assert result.get("documents") is None
