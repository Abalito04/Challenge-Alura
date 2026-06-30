from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable


SYSTEM_PROMPT = """Sos Medinova AI Agent, un asistente administrativo documental.
Respondé únicamente con hechos presentes en el contexto proporcionado.
Contestá exactamente lo preguntado y omití reglas relacionadas que no sean necesarias.
No diagnostiques, no interpretes síntomas o resultados y no indiques tratamientos o medicación.
Si el contexto solo responde una parte, aclaralo. Si no responde, indicá que la documentación
no contiene información suficiente. No inventes horarios, coberturas, disponibilidad ni reglas.
Usá español claro, profesional y conciso. No agregues una lista de fuentes: la aplicación la
adjunta de forma verificable después de tu respuesta."""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Conversación reciente:\n{conversation}\n\nPregunta actual:\n{question}"
            "\n\nContexto institucional:\n{context}",
        ),
    ]
)


@dataclass(frozen=True)
class Citation:
    source: str
    page: int | None


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    citations: tuple[Citation, ...]


def _format_context(documents: tuple[Document, ...]) -> str:
    blocks = []
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "fuente desconocida")
        page = document.metadata.get("page")
        blocks.append(
            f"[Fragmento {index} | Fuente: {source} | Página: {page}]\n"
            f"{document.page_content}"
        )
    return "\n\n".join(blocks)


def _citations(documents: tuple[Document, ...]) -> tuple[Citation, ...]:
    seen: set[tuple[str, int | None]] = set()
    citations: list[Citation] = []
    for document in documents:
        key = (str(document.metadata.get("source", "fuente desconocida")), document.metadata.get("page"))
        if key not in seen:
            seen.add(key)
            citations.append(Citation(*key))
    return tuple(citations)


def generate_grounded_answer(
    llm: Runnable,
    *,
    question: str,
    documents: tuple[Document, ...],
    conversation: tuple[dict[str, str], ...] = (),
) -> GroundedAnswer:
    if not documents:
        return GroundedAnswer(
            "La documentación institucional disponible no contiene información suficiente para responder esa consulta.",
            (),
        )
    chain = PROMPT | llm | StrOutputParser()
    conversation_text = "\n".join(
        f"{item.get('role', 'usuario')}: {item.get('content', '')}"
        for item in conversation[-6:]
    ) or "Sin conversación previa."
    text = chain.invoke(
        {
            "question": question,
            "context": _format_context(documents),
            "conversation": conversation_text,
        }
    )
    return GroundedAnswer(text=text.strip(), citations=_citations(documents))
