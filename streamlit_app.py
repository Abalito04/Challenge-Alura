from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from app.agent.classification import classify_intent
from app.agent.graph import build_agent_graph
from app.agent.quick_responses import quick_response_for_intent
from app.appointments import append_request, create_request, load_requests
from app.chat_history import clear_chat_history, load_chat_history, save_chat_history
from app.config import get_settings
from app.llm_provider import create_chat_model
from app.rag.embeddings import create_embeddings
from app.rag.pipeline import ingest_corpus
from app.rag.vectorstore import open_vectorstore


st.set_page_config(
    page_title="Medinova AI Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto",
)


def apply_theme(mode: str) -> None:
    if mode == "Oscuro":
        palette = {
            "app_bg": "#111816",
            "surface": "#17211e",
            "surface_soft": "#1f2d29",
            "text": "#eef2ed",
            "muted": "#aebbb4",
            "line": "#34443f",
            "chat_bg": "#182520",
            "citation": "#cbd8d0",
            "step": "#d9e4de",
            "teal": "#8fb7a5",
            "teal_hover": "#7aa593",
            "input_bg": "#121d1a",
            "input_shell": "#1d2a26",
            "input_border": "#4a6259",
            "uploader_bg": "#1c2925",
            "uploader_text": "#d7e1dc",
            "shadow": "0 18px 45px rgba(0,0,0,.32)",
        }
    else:
        palette = {
            "app_bg": "#faf8f3",
            "surface": "#fffdf8",
            "surface_soft": "#f0f4ee",
            "text": "#26352f",
            "muted": "#6f7f76",
            "line": "#d9dfd4",
            "chat_bg": "#fffdf8",
            "citation": "#52665c",
            "step": "#40554b",
            "teal": "#6f9f8b",
            "teal_hover": "#5e8d7a",
            "input_bg": "#fffefa",
            "input_shell": "#f1f5ef",
            "input_border": "#c5d0c4",
            "uploader_bg": "#f3f6f0",
            "uploader_text": "#52665c",
            "shadow": "0 16px 38px rgba(60,76,67,.12)",
        }
    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg:{palette["app_bg"]};
            --surface:{palette["surface"]};
            --surface-soft:{palette["surface_soft"]};
            --text:{palette["text"]};
            --muted:{palette["muted"]};
            --line:{palette["line"]};
            --chat-bg:{palette["chat_bg"]};
            --citation:{palette["citation"]};
            --step:{palette["step"]};
            --teal:{palette["teal"]};
            --teal-hover:{palette["teal_hover"]};
            --input-bg:{palette["input_bg"]};
            --input-shell:{palette["input_shell"]};
            --input-border:{palette["input_border"]};
            --uploader-bg:{palette["uploader_bg"]};
            --uploader-text:{palette["uploader_text"]};
            --shadow:{palette["shadow"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    .stApp { background:var(--app-bg); color:var(--text); }
    [data-testid="stHeader"] { background:var(--surface); border-bottom:1px solid var(--line); }
    [data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] h1 { color:var(--text); font-size:1.55rem; }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top:1.25rem;
    }
    .sidebar-brand {
        border:1px solid var(--line);
        border-radius:18px;
        background:linear-gradient(180deg, var(--surface), var(--surface-soft));
        padding:1rem 1rem .95rem;
        margin:.25rem 0 1rem;
    }
    .brand-kicker {
        color:var(--teal);
        font-size:.78rem;
        font-weight:700;
        letter-spacing:.08em;
        text-transform:uppercase;
        margin-bottom:.35rem;
    }
    .brand-title {
        color:var(--text);
        font-size:1.35rem;
        line-height:1.1;
        font-weight:800;
        letter-spacing:-.03em;
        margin:0;
    }
    .brand-subtitle {
        color:var(--muted);
        font-size:.83rem;
        margin-top:.45rem;
    }
    .sidebar-section-title {
        color:var(--muted);
        font-size:.74rem;
        font-weight:700;
        letter-spacing:.08em;
        text-transform:uppercase;
        margin:.9rem 0 .35rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        border:1px solid var(--line);
        border-radius:16px;
        background:var(--surface-soft);
        padding:.65rem .75rem .55rem;
        margin-bottom:.8rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color:var(--text) !important;
    }
    [data-testid="stSidebar"] hr {
        margin:1rem 0;
        border-color:var(--line);
    }
    .sidebar-actions {
        border:1px solid var(--line);
        border-radius:16px;
        background:var(--surface-soft);
        padding:.75rem;
        margin-top:.85rem;
    }
    .block-container { padding-top:1.9rem; max-width:1500px; }
    h1,h2,h3 { color:var(--text); letter-spacing:-.02em; }
    p, li, label, span, div { color:var(--text); }
    .provider-line { color:var(--muted); font-size:.88rem; margin-bottom:1.25rem; }
    .trace {
        position:sticky;
        top:4rem;
        border-left:1px solid var(--line);
        padding-left:1.4rem;
        max-height:calc(100vh - 5rem);
        overflow:auto;
    }
    .trace-step { padding:.52rem 0; border-bottom:1px solid var(--line); color:var(--step); }
    .trace-step strong { color:var(--teal); margin-right:.45rem; }
    .citation { padding:.72rem .85rem; border-top:1px solid var(--line); color:var(--citation); }
    .citation:first-child { border-top:0; }
    .small-note { color:var(--muted); font-size:.85rem; }
    .stButton > button,
    .stFormSubmitButton > button {
        background:var(--teal) !important;
        border-color:var(--teal) !important;
        color:#fff !important;
    }
    .stButton > button *,
    .stFormSubmitButton > button *,
    .stButton > button p,
    .stFormSubmitButton > button p,
    .stButton > button span,
    .stFormSubmitButton > button span {
        color:#fff !important;
        opacity:1 !important;
        visibility:visible !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background:var(--teal-hover) !important;
        border-color:var(--teal-hover) !important;
        color:#fff !important;
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background:var(--teal) !important;
        border-color:var(--teal) !important;
        color:#fff !important;
    }
    .stButton > button[kind="primary"] *,
    .stFormSubmitButton > button[kind="primary"] *,
    button[data-testid="baseButton-primary"] *,
    button[data-testid="baseButton-primary"] p,
    button[data-testid="baseButton-primary"] span {
        color:#fff !important;
        opacity:1 !important;
        visibility:visible !important;
    }
    [data-testid="stChatMessage"] {
        border:1px solid var(--line);
        border-radius:12px;
        background:var(--chat-bg);
    }
    [data-testid="stChatMessage"] * { color:var(--text); }
    [data-testid="stMarkdownContainer"] code {
        background:var(--surface-soft);
        color:var(--teal);
        border:1px solid var(--line);
    }
    input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
        background:var(--input-bg) !important;
        color:var(--text) !important;
    }
    [data-baseweb="input"], [data-baseweb="textarea"] {
        background:var(--input-bg) !important;
        border-color:var(--line) !important;
    }
    [data-testid="stChatInput"] {
        background:transparent !important;
        margin-top:1.3rem !important;
    }
    [data-testid="stChatInput"] > div {
        background:var(--input-shell) !important;
        border:1px solid var(--input-border) !important;
        border-radius:24px !important;
        box-shadow:var(--shadow);
        padding:.55rem .62rem !important;
        min-height:68px !important;
        display:flex !important;
        align-items:center !important;
    }
    [data-testid="stChatInput"] [data-baseweb="textarea"] {
        background:var(--input-bg) !important;
        border:1px solid var(--input-border) !important;
        border-radius:18px !important;
        min-height:48px !important;
        display:flex !important;
        align-items:center !important;
    }
    [data-testid="stChatInput"] textarea {
        background:var(--input-bg) !important;
        color:var(--text) !important;
        caret-color:var(--teal) !important;
        min-height:46px !important;
        padding:.72rem 1rem !important;
        font-size:1rem !important;
        line-height:1.35 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color:var(--muted) !important;
        opacity:.9 !important;
    }
    [data-testid="stChatInput"] button {
        background:var(--teal) !important;
        border:1px solid var(--teal) !important;
        border-radius:16px !important;
        color:#fff !important;
        width:48px !important;
        height:48px !important;
        min-width:48px !important;
        margin-left:.55rem !important;
        box-shadow:0 10px 22px rgba(80,112,96,.22);
    }
    [data-testid="stChatInput"] button:hover {
        background:var(--teal-hover) !important;
        border-color:var(--teal-hover) !important;
        transform:translateY(-1px);
    }
    [data-testid="stChatInput"] button svg,
    [data-testid="stChatInput"] button svg path {
        color:#fff !important;
        fill:none !important;
        stroke:#fff !important;
        stroke-width:2.4 !important;
    }
    [data-testid="stForm"] {
        border:1px solid var(--input-border) !important;
        border-radius:22px !important;
        background:var(--input-shell) !important;
        box-shadow:var(--shadow);
        padding:.8rem .9rem !important;
    }
    [data-testid="InputInstructions"] {
        display:none !important;
    }
    .chat-history-label {
        color:var(--muted);
        font-size:.78rem;
        font-weight:700;
        letter-spacing:.08em;
        text-transform:uppercase;
        margin:.45rem 0 .8rem;
    }
    [data-testid="stFileUploader"] section {
        background:var(--uploader-bg) !important;
        border:1px solid var(--input-border) !important;
        border-radius:12px !important;
    }
    [data-testid="stFileUploader"] section * {
        color:var(--uploader-text) !important;
    }
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button[kind="secondary"] {
        background:var(--teal) !important;
        border-color:var(--teal) !important;
        color:#fff !important;
    }
    [data-testid="stFileUploader"] button *,
    [data-testid="stFileUploader"] button p,
    [data-testid="stFileUploader"] button span,
    [data-testid="stFileUploader"] button svg,
    [data-testid="stFileUploader"] button svg path {
        color:#fff !important;
        fill:#fff !important;
        stroke:#fff !important;
        opacity:1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


RUNTIME_VERSION = "quick-responses-v4"
CHAT_HISTORY_PATH = Path("data/chat_history.json")


def handle_prompt(prompt: str, graph) -> None:
    conversation = tuple(
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages[-8:]
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_history(CHAT_HISTORY_PATH, st.session_state.messages)
    with st.spinner("LangGraph está consultando el corpus..."):
        try:
            st.session_state.pop("provider_error", None)
            result = graph.invoke({"question": prompt, "conversation": conversation})
        except Exception as exc:
            simple_result = local_simple_answer(prompt)
            if simple_result:
                result = simple_result
            else:
                st.session_state.last_result = {
                    "intent": "invalid",
                    "documents": (),
                    "answer": "No se pudo completar la consulta.",
                    "citations": (),
                }
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            "No pude completar la consulta con el proveedor de IA en este momento. "
                            "Probá nuevamente en unos segundos o revisá la cuota/API key configurada."
                        ),
                        "citations": (),
                        "intent": "invalid",
                        "id": len(st.session_state.messages),
                    }
                )
                save_chat_history(CHAT_HISTORY_PATH, st.session_state.messages)
                st.session_state.provider_error = str(exc)
                st.rerun()
                return
    st.session_state.last_result = result
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "citations": result.get("citations", ()),
            "intent": result.get("intent"),
            "appointment_professional": result.get("appointment_professional", ""),
            "appointment_specialty": result.get("appointment_specialty", ""),
            "id": len(st.session_state.messages),
        }
    )
    save_chat_history(CHAT_HISTORY_PATH, st.session_state.messages)
    st.rerun()


def safe_pdf_name(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9áéíóúñü]+", "_", stem, flags=re.IGNORECASE).strip("_")
    return f"{stem or 'documento'}{Path(filename).suffix.lower() or '.pdf'}"


def unique_document_path(directory: Path, filename: str) -> Path:
    candidate = directory / safe_pdf_name(filename)
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        numbered = directory / f"{stem}_{index}{suffix}"
        if not numbered.exists():
            return numbered
        index += 1


def local_simple_answer(prompt: str) -> dict | None:
    intent = classify_intent(prompt)
    response = quick_response_for_intent(intent, question=prompt)
    if response is None:
        return None
    result = response.as_state()
    result["intent"] = intent
    result["documents"] = ()
    return result


@st.cache_resource(show_spinner="Preparando el agente RAG...")
def build_runtime(version: str = RUNTIME_VERSION):
    del version  # La versión invalida la caché cuando cambia el grafo.
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
        steps.extend(["Contextualizar seguimiento", "Recuperar documentos", "Evaluar evidencia"])
        steps.append("Generar respuesta" if result.get("sufficient") else "Respuesta insuficiente")
    elif intent == "clinical":
        steps.append("Aplicar guardrail clínico")
    elif intent == "appointment":
        steps.append("Derivar a solicitudes")
    elif intent == "directory":
        steps.append("Responder directorio institucional")
    elif intent == "admin_policy":
        steps.append("Responder política administrativa")
    elif intent == "location":
        steps.append("Responder ubicación/sedes")
    elif intent == "greeting":
        steps.append("Responder conversación breve")
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
    try:
        settings, graph = build_runtime(RUNTIME_VERSION)
    except Exception as exc:
        st.title("Asistente documental")
        st.error("No se pudo inicializar el agente RAG.")
        st.info(
            "Revisá que exista el archivo `.env` en la raíz del proyecto y que incluya "
            "las API keys configuradas para LLM y embeddings."
        )
        with st.expander("Detalle técnico"):
            st.code(str(exc))
        st.markdown(
            """
            Ejemplo mínimo recomendado:

            ```env
            LLM_PROVIDER=cohere
            LLM_MODEL=command-a-03-2025
            LLM_FALLBACK_PROVIDER=gemini
            LLM_FALLBACK_MODEL=gemini-2.5-flash
            EMBEDDINGS_PROVIDER=cohere
            EMBEDDINGS_MODEL=embed-v4.0
            COHERE_API_KEY=tu_key_de_cohere
            GEMINI_API_KEY=tu_key_de_gemini
            DOCUMENT_UPLOAD_PASSWORD=la_clave_que_quieras
            ```
            """
        )
        return
    main, technical = st.columns([2.35, 0.8], gap="large")
    with main:
        st.title("Asistente documental")
        st.markdown(
            '<p class="provider-line">Respuestas institucionales basadas en los PDF de Medinova, con fuentes verificables.</p>',
            unsafe_allow_html=True,
        )
        if st.session_state.get("provider_error"):
            with st.expander("Último error técnico del proveedor"):
                st.code(st.session_state.provider_error)
        if "messages" not in st.session_state:
            st.session_state.messages = load_chat_history(CHAT_HISTORY_PATH)
        with st.form("top_chat_composer", clear_on_submit=True, border=False):
            input_col, send_col = st.columns([7, 1], vertical_alignment="center")
            with input_col:
                prompt = st.text_input(
                    "Consulta",
                    placeholder="Escribí tu consulta sobre Medinova",
                    label_visibility="collapsed",
                )
            with send_col:
                submitted = st.form_submit_button("Enviar", use_container_width=True)
        if submitted and prompt.strip():
            handle_prompt(prompt.strip(), graph)
        if st.session_state.messages:
            st.markdown(
                '<div class="chat-history-label">Conversación reciente</div>',
                unsafe_allow_html=True,
            )
        for message in reversed(st.session_state.messages):
            avatar = "👤" if message["role"] == "user" else "🩺"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                if message.get("citations"):
                    st.markdown("**Fuentes consultadas**")
                    for citation in message["citations"]:
                        page = citation.get("page")
                        st.markdown(
                            f'<div class="citation">📄 {citation["source"]} · página {page}</div>',
                            unsafe_allow_html=True,
                        )
                if message.get("intent") == "appointment":
                    st.button(
                        "Ir a Solicitudes",
                        key=f"request_{message.get('id', id(message))}",
                        on_click=go_to_requests,
                        args=(
                            message.get("appointment_professional", ""),
                            message.get("appointment_specialty", ""),
                        ),
                    )
    with technical:
        render_trace(settings, st.session_state.get("last_result"))


def render_documents() -> None:
    settings = get_settings()
    st.title("Documentos del corpus")
    st.write("Los PDF versionados son la fuente de verdad del RAG.")
    files = sorted(settings.source_documents_dir.glob("*.pdf"))
    for file in files:
        st.markdown(f"📄 **{file.name}**")
    st.divider()
    st.subheader("Carga protegida de documentos")
    st.caption(
        "Solo personal autorizado puede agregar PDFs al corpus. "
        "Al cargar un archivo, el índice RAG se actualiza automáticamente."
    )
    if not settings.document_upload_password:
        st.warning(
            "Configurá DOCUMENT_UPLOAD_PASSWORD en el archivo .env para habilitar la carga."
        )
        return
    with st.form("protected_document_upload", clear_on_submit=True):
        password = st.text_input("Contraseña de carga", type="password")
        uploaded = st.file_uploader("Seleccionar PDF", type="pdf")
        submitted = st.form_submit_button("Cargar e indexar PDF")
    if submitted:
        if password != settings.document_upload_password:
            st.error("Contraseña incorrecta.")
            return
        if uploaded is None:
            st.error("Seleccioná un archivo PDF.")
            return
        content = uploaded.getvalue()
        if not content.startswith(b"%PDF"):
            st.error("El archivo seleccionado no parece ser un PDF válido.")
            return
        settings.source_documents_dir.mkdir(parents=True, exist_ok=True)
        destination = unique_document_path(settings.source_documents_dir, uploaded.name)
        destination.write_bytes(content)
        with st.spinner("Indexando el corpus actualizado..."):
            result = ingest_corpus(settings)
        build_runtime.clear()
        st.session_state.pop("last_result", None)
        st.success(
            "PDF cargado e indexado: "
            f"{destination.name}. Corpus: {result.files} archivos, "
            f"{result.pages} páginas, {result.chunks} fragmentos."
        )


def render_requests() -> None:
    st.title("Solicitudes de turno")
    st.info("Una solicitud queda pendiente hasta que el equipo de admisión confirme fecha, hora y sede.")
    path = Path("data/turnos_solicitudes.csv")
    request_tab, panel_tab = st.tabs(["Nueva solicitud", "Panel básico"])
    with request_tab:
        with st.form("appointment_request", clear_on_submit=True):
            name = st.text_input("Nombre y apellido")
            contact = st.text_input("Contacto")
            specialty = st.text_input(
                "Especialidad",
                value=st.session_state.get("appointment_specialty", ""),
            )
            preferred = st.text_input("Preferencia horaria")
            professional = st.session_state.get("appointment_professional", "")
            notes = st.text_area(
                "Observaciones",
                value=(f"Profesional solicitado: {professional}" if professional else ""),
                max_chars=300,
            )
            submitted = st.form_submit_button("Registrar solicitud pendiente")
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


def go_to_requests(professional: str = "", specialty: str = "") -> None:
    st.session_state.appointment_professional = professional
    st.session_state.appointment_specialty = specialty
    st.session_state.navigation = "Solicitudes"


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-kicker">Clínica Medinova</div>
            <div class="brand-title">Medinova AI Agent</div>
            <div class="brand-subtitle">RAG · LangChain · LangGraph · Chroma</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section-title">Preferencias</div>', unsafe_allow_html=True)
    theme = st.radio(
        "Tema",
        ("Claro", "Oscuro"),
        horizontal=True,
        key="theme_mode",
        label_visibility="collapsed",
    )
    apply_theme(theme)
    st.markdown('<div class="sidebar-section-title">Navegación</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navegación",
        ("Asistente", "Documentos", "Solicitudes"),
        label_visibility="collapsed",
        key="navigation",
    )
    st.markdown('<div class="sidebar-section-title">Acciones</div>', unsafe_allow_html=True)
    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("last_result", None)
        clear_chat_history(CHAT_HISTORY_PATH)
        st.rerun()
    if st.button("Eliminar todo el chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("last_result", None)
        st.session_state.pop("provider_error", None)
        clear_chat_history(CHAT_HISTORY_PATH)
        st.success("Chat eliminado.")
        st.rerun()

if page == "Asistente":
    render_assistant()
elif page == "Documentos":
    render_documents()
else:
    render_requests()
