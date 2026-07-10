from __future__ import annotations

import re
from typing import Any, Literal, TypedDict

from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from app.agent.classification import Intent, classify_intent
from app.rag.answering import generate_grounded_answer
from app.rag.retrieval import retrieve_context


class AgentState(TypedDict, total=False):
    question: str
    conversation: tuple[dict[str, str], ...]
    retrieval_question: str
    intent: Intent
    documents: tuple[Document, ...]
    scores: tuple[float, ...]
    sufficient: bool
    answer: str
    citations: tuple[dict[str, Any], ...]
    appointment_professional: str
    appointment_specialty: str


def build_agent_graph(
    *,
    vectorstore: Any,
    llm: Runnable,
    retrieval_k: int = 5,
    score_threshold: float = 0.25,
):
    def history_text(state: AgentState) -> str:
        return "\n".join(
            item.get("content", "") for item in state.get("conversation", ())[-6:]
        )

    def contextualize_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()
        previous_user_questions = [
            item.get("content", "").strip()
            for item in state.get("conversation", ())
            if item.get("role") == "user" and item.get("content", "").strip()
        ]
        follow_up = bool(
            previous_user_questions
            and (
                len(question.split()) <= 12
                or question.casefold().startswith(
                    ("y ", "también", "además", "qué ", "cuándo", "dónde", "cuál", "cómo")
                )
            )
        )
        if follow_up:
            question = (
                f"Consulta anterior: {previous_user_questions[-1]}\n"
                f"Pregunta de seguimiento: {question}"
            )
        return {"retrieval_question": question}

    def classify_node(state: AgentState) -> AgentState:
        return {
            "intent": classify_intent(
                state.get("question", ""), history_text=history_text(state)
            )
        }

    def route_intent(
        state: AgentState,
    ) -> Literal["retrieve", "clinical", "appointment", "greeting", "invalid"]:
        mapping = {
            "documental": "retrieve",
            "clinical": "clinical",
            "appointment": "appointment",
            "greeting": "greeting",
            "invalid": "invalid",
        }
        return mapping[state["intent"]]

    def retrieve_node(state: AgentState) -> AgentState:
        result = retrieve_context(
            vectorstore,
            state.get("retrieval_question", state["question"]),
            k=retrieval_k,
            score_threshold=score_threshold,
        )
        return {
            "documents": result.documents,
            "scores": result.scores,
            "sufficient": result.sufficient,
        }

    def route_evidence(state: AgentState) -> Literal["generate", "insufficient"]:
        return "generate" if state.get("sufficient") else "insufficient"

    def generate_node(state: AgentState) -> AgentState:
        result = generate_grounded_answer(
            llm,
            question=state["question"],
            documents=state["documents"],
            conversation=state.get("conversation", ()),
        )
        return {
            "answer": result.text,
            "citations": tuple(
                {"source": citation.source, "page": citation.page}
                for citation in result.citations
            ),
        }

    def clinical_node(_: AgentState) -> AgentState:
        return {
            "answer": (
                "No puedo brindar diagnósticos, interpretar síntomas o resultados, ni indicar "
                "medicación o tratamientos. Consultá con un profesional de salud o con el canal "
                "correspondiente de la clínica."
            ),
            "citations": (),
        }

    def appointment_node(state: AgentState) -> AgentState:
        context = "\n".join(
            item.get("content", "") for item in state.get("conversation", ())[-8:]
        )
        professionals = re.findall(
            r"\b(?:Dra?\.)\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]+){1,2}",
            context,
        )
        professional = professionals[-1] if professionals else ""
        specialty = "Cardiología" if re.search(r"cardiolog", context, re.IGNORECASE) else ""
        detail = ""
        if professional:
            detail = f" para {professional}"
        elif specialty:
            detail = f" para {specialty}"
        return {
            "answer": (
                f"Sí. Puedo derivarte al formulario de la sección Solicitudes{detail}. "
                "Completá los datos de contacto y preferencia horaria. La solicitud quedará "
                "registrada como pendiente; no confirma una reserva ni asigna automáticamente un turno."
            ),
            "citations": (),
            "appointment_professional": professional,
            "appointment_specialty": specialty,
        }

    def greeting_node(_: AgentState) -> AgentState:
        return {
            "answer": (
                "¡Hola! Soy Medinova AI Agent. Puedo ayudarte con información institucional, "
                "especialistas, sedes, horarios, coberturas y políticas disponibles en los "
                "documentos de la clínica. ¿Qué necesitás consultar?"
            ),
            "citations": (),
        }

    def invalid_node(_: AgentState) -> AgentState:
        return {"answer": "Ingresá una consulta válida para poder ayudarte.", "citations": ()}

    def insufficient_node(_: AgentState) -> AgentState:
        return {
            "answer": "La documentación institucional disponible no contiene información suficiente para responder esa consulta.",
            "citations": (),
        }

    builder = StateGraph(AgentState)
    builder.add_node("classify", classify_node)
    builder.add_node("contextualize", contextualize_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_node("clinical", clinical_node)
    builder.add_node("appointment", appointment_node)
    builder.add_node("greeting", greeting_node)
    builder.add_node("invalid", invalid_node)
    builder.add_node("insufficient", insufficient_node)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_intent,
        {
            "retrieve": "contextualize",
            "clinical": "clinical",
            "appointment": "appointment",
            "greeting": "greeting",
            "invalid": "invalid",
        },
    )
    builder.add_edge("contextualize", "retrieve")
    builder.add_conditional_edges("retrieve", route_evidence)
    for terminal in (
        "generate",
        "clinical",
        "appointment",
        "greeting",
        "invalid",
        "insufficient",
    ):
        builder.add_edge(terminal, END)
    return builder.compile()
