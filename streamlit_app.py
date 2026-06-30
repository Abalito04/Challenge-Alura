from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.agent.graph import build_agent_graph
from app.appointments import append_request, create_request, load_requests
from app.config import get_settings
from app.llm_provider import create_chat_model
from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import open_vectorstore


st.set_page_config(
    page_title="Medinova AI Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    :root { --navy:#0b2c50; --teal:#078b83; --line:#dbe5ec; --soft:#f4f8fa; }
    .stApp { background:#fff; color:var(--navy); }
    [data-testid="stHeader"] { background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); }
    [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] h1 { color:var(--navy); font-size:1.55rem; }
    .block-container { padding-top:1.9rem; max-width:1500px; }
    h1,h2,h3 { color:var(--navy); letter-spacing:-.02em; }
    .provider-line { color:#52697e; font-size:.88rem; margin-bottom:1.25rem; }
    .trace { border-left:1px solid var(--line); padding-left:1.4rem; min-height:68vh; }
    .trace-step { padding:.52rem 0; border-bottom:1px solid #edf2f5; color:#1f4669; }
    .trace-step strong { color:var(--teal); margin-right:.45rem; }
    .citation { padding:.72rem .85rem; border-top:1px solid var(--line); color:#31536f; }
    .citation:first-child { border-top:0; }
    .small-note { color:#61798d; font-size:.85rem; }
    .stButton > button, .stFormSubmitButton > button { border-color:var(--teal); color:var(--teal); }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:var(--teal); color:white; }
    [data-testid="stChatMessage"] { border:1px solid #e5edf2; border-radius:12px; background:#fbfdfe; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Preparando el agente RAG...")
def build_runtime():
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
    return settings, graph


def trace_for(result: dict) -> list[str]:
    intent = result.get("intent", "invalid")
    steps = ["Clasificar intención"]
    if intent == "documental":
        steps.extend(["Recuperar documentos", "Evaluar evidencia"])
        steps.append("Generar respuesta" if result.get("sufficient") else "Respuesta insuficiente")
    elif intent == "clinical":
        steps.append("Aplicar guardrail clínico")
    elif intent == "appointment":
        steps.append("Derivar a solicitudes")
    else:
        steps.append("Validar entrada")
    return steps


def render_trace(settings, result: dict | None) -> None:
    st.markdown('<div class="trace">', unsafe_allow_html=True)
    st.subheader("Flujo técnico")
    if result:
        for index, step in enumerate(trace_for(result), start=1):
            st.markdown(
                f'<div class="trace-step"><strong>{index:02}</strong>{step}</div>',
                unsafe_allow_html=True,
            )
        st.metric("Fragmentos recuperados", len(result.get("documents", ())))
    else:
        st.caption("El recorrido de LangGraph aparecerá después de una consulta.")
    st.divider()
    st.markdown(
        f"**LLM**<br>{settings.llm_provider} · `{settings.llm_model}`",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Embeddings**<br>{settings.embeddings_provider} · `{settings.embeddings_model}`",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Frameworks**<br>LangChain · LangGraph · Chroma",
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


def render_assistant() -> None:
    settings, graph = build_runtime()
    main, technical = st.columns([2.35, 0.8], gap="large")
    with main:
        st.title("Asistente documental")
        st.markdown(
            '<p class="provider-line">Respuestas institucionales basadas en los PDF de Medinova, con fuentes verificables.</p>',
            unsafe_allow_html=True,
        )
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("citations"):
                    st.markdown("**Fuentes consultadas**")
                    for citation in message["citations"]:
                        page = citation.get("page")
                        st.markdown(
                            f'<div class="citation">📄 {citation["source"]} · página {page}</div>',
                            unsafe_allow_html=True,
                        )
        prompt = st.chat_input("Escribí tu consulta sobre Medinova")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("LangGraph está consultando el corpus..."):
                try:
                    result = graph.invoke({"question": prompt})
                except Exception as exc:
                    st.error(f"No se pudo completar la consulta: {exc}")
                    return
            st.session_state.last_result = result
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "citations": result.get("citations", ()),
                }
            )
            st.rerun()
    with technical:
        render_trace(settings, st.session_state.get("last_result"))


def render_documents() -> None:
    st.title("Documentos del corpus")
    st.write("Los PDF versionados son la fuente de verdad del RAG.")
    files = sorted(Path("source_documents").glob("*.pdf"))
    for file in files:
        st.markdown(f"📄 **{file.name}**")
    st.divider()
    st.file_uploader(
        "Agregar PDF en una evolución futura",
        type="pdf",
        disabled=True,
        help="La carga dinámica requiere validación, permisos y reindexado controlado.",
    )


def render_requests() -> None:
    st.title("Solicitudes de turno")
    st.warning("Demostración: usá únicamente datos ficticios. Una solicitud no confirma un turno.")
    path = Path("data/turnos_solicitudes.csv")
    request_tab, panel_tab = st.tabs(["Nueva solicitud", "Panel básico"])
    with request_tab:
        with st.form("appointment_request", clear_on_submit=True):
            name = st.text_input("Nombre ficticio")
            contact = st.text_input("Contacto ficticio")
            specialty = st.text_input("Especialidad")
            preferred = st.text_input("Preferencia horaria")
            notes = st.text_area("Observaciones", max_chars=300)
            submitted = st.form_submit_button("Registrar solicitud pendiente", type="primary")
        if submitted:
            try:
                request = create_request(
                    patient_name=name,
                    contact=contact,
                    specialty=specialty,
                    preferred_time=preferred,
                    notes=notes,
                )
                append_request(path, request)
                st.success(f"Solicitud {request.request_id} registrada como pendiente.")
            except ValueError as exc:
                st.error(str(exc))
    with panel_tab:
        rows = load_requests(path)
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay solicitudes de demostración.")


with st.sidebar:
    st.title("Medinova AI Agent")
    st.caption("RAG · LangChain · LangGraph")
    page = st.radio(
        "Navegación",
        ("Asistente", "Documentos", "Solicitudes"),
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("last_result", None)
        st.rerun()

if page == "Asistente":
    render_assistant()
elif page == "Documentos":
    render_documents()
else:
    render_requests()
