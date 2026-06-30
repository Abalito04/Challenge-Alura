from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from app.agent.classification import Intent, classify_intent
from app.rag.answering import generate_grounded_answer
from app.rag.retrieval import retrieve_context


class AgentState(TypedDict, total=False):
    question: str
    intent: Intent
    documents: tuple[Document, ...]
    scores: tuple[float, ...]
    sufficient: bool
    answer: str
    citations: tuple[dict[str, Any], ...]


def build_agent_graph(
    *,
    vectorstore: Any,
    llm: Runnable,
    retrieval_k: int = 5,
    score_threshold: float = 0.25,
):
    def classify_node(state: AgentState) -> AgentState:
        return {"intent": classify_intent(state.get("question", ""))}

    def route_intent(state: AgentState) -> Literal["retrieve", "clinical", "appointment", "invalid"]:
        mapping = {
            "documental": "retrieve",
            "clinical": "clinical",
            "appointment": "appointment",
            "invalid": "invalid",
        }
        return mapping[state["intent"]]

    def retrieve_node(state: AgentState) -> AgentState:
        result = retrieve_context(
            vectorstore,
            state["question"],
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

    def appointment_node(_: AgentState) -> AgentState:
        return {
            "answer": (
                "Puedo ayudarte a registrar una solicitud de turno pendiente. El formulario y "
                "su persistencia se incorporarán en la siguiente etapa; esto no confirma una reserva."
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
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_node("clinical", clinical_node)
    builder.add_node("appointment", appointment_node)
    builder.add_node("invalid", invalid_node)
    builder.add_node("insufficient", insufficient_node)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route_intent)
    builder.add_conditional_edges("retrieve", route_evidence)
    for terminal in ("generate", "clinical", "appointment", "invalid", "insufficient"):
        builder.add_edge(terminal, END)
    return builder.compile()
