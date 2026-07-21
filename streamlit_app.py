"""
Interfaz Streamlit del agente RAG.

Secciones:
  1. Subir documentos  →  POST /api/v1/documents/upload
  2. Chat con el agente →  POST /api/v1/chat/query
  3. Documentos indexados → GET /api/v1/documents
"""

import os

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
UPLOAD_URL = f"{API_BASE}/api/v1/documents/upload"
QUERY_URL = f"{API_BASE}/api/v1/chat/query"
FEEDBACK_URL = f"{API_BASE}/api/v1/chat/feedback"
DOCS_URL = f"{API_BASE}/api/v1/documents"

st.set_page_config(
    page_title="Agente RAG — Documentos Internos",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []       # [{role, content, sources, feedback_sent}]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _post_feedback(question: str, feedback: str) -> None:
    try:
        requests.post(FEEDBACK_URL, json={"question": question, "feedback": feedback}, timeout=5)
    except Exception:
        pass


def _upload_file(file_bytes: bytes, filename: str) -> dict | None:
    try:
        resp = requests.post(
            UPLOAD_URL,
            files={"file": (filename, file_bytes)},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        st.error(f"Error al subir el archivo: {e.response.text}")
    except Exception as e:
        st.error(f"No se pudo conectar con la API: {e}")
    return None


def _query_agent(question: str) -> dict | None:
    try:
        resp = requests.post(QUERY_URL, json={"question": question}, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        st.error(f"Error del agente: {e.response.text}")
    except Exception as e:
        st.error(f"No se pudo conectar con la API: {e}")
    return None


def _fetch_documents() -> list[dict]:
    try:
        resp = requests.get(DOCS_URL, timeout=10)
        resp.raise_for_status()
        return resp.json().get("documents", [])
    except Exception:
        return []


def _render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    st.markdown("**📄 Fuentes:**")
    for src in sources:
        parts = [f"`{src['document']}`"]
        if src.get("section"):
            parts.append(f"— {src['section']}")
        if src.get("page"):
            parts.append(f"(pág. {src['page']})")
        elif src.get("slide"):
            parts.append(f"(diap. {src['slide']})")
        st.markdown("  • " + " ".join(parts))


# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

st.title("🤖 Agente de IA — Documentos Internos")
st.caption(
    "Estás hablando con un **agente de IA** basado en Qwen3. "
    "Sus respuestas se basan únicamente en los documentos que hayas subido."
)

col_chat, col_sidebar = st.columns([3, 1])

# ---------------------------------------------------------------------------
# Columna lateral — subida + lista de documentos
# ---------------------------------------------------------------------------

with col_sidebar:
    st.subheader("📁 Subir documento")

    uploaded = st.file_uploader(
        "Elige un archivo",
        type=["pdf", "docx", "xlsx", "pptx", "md", "csv", "json", "html", "txt"],
        label_visibility="collapsed",
    )

    if uploaded is not None:
        if st.button("⬆️ Indexar documento", use_container_width=True):
            with st.spinner(f"Procesando *{uploaded.name}*…"):
                result = _upload_file(uploaded.read(), uploaded.name)
            if result:
                st.success(
                    f"✅ **{result['filename']}** indexado  \n"
                    f"{result['chunk_count']} fragmentos guardados."
                )

    st.divider()
    st.subheader("📚 Documentos indexados")

    if st.button("🔄 Actualizar lista", use_container_width=True):
        st.session_state["docs_cache"] = _fetch_documents()

    docs = st.session_state.get("docs_cache") or _fetch_documents()
    st.session_state["docs_cache"] = docs

    if docs:
        for doc in docs:
            st.markdown(
                f"**{doc['filename']}**  \n"
                f"`{doc['document_type'].upper()}` · {doc['chunk_count']} fragmentos"
            )
    else:
        st.info("Aún no hay documentos indexados.")

# ---------------------------------------------------------------------------
# Columna principal — chat
# ---------------------------------------------------------------------------

with col_chat:
    st.subheader("💬 Chat con el agente")

    # Renderizar historial
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Fuentes (solo mensajes del asistente)
            if msg["role"] == "assistant" and msg.get("sources"):
                _render_sources(msg["sources"])

            # Feedback (solo mensajes del asistente que aún no lo tienen)
            if msg["role"] == "assistant" and not msg.get("feedback_sent"):
                fb_col1, fb_col2, _ = st.columns([1, 1, 8])
                with fb_col1:
                    if st.button("👍", key=f"pos_{i}"):
                        _post_feedback(msg.get("question", ""), "positive")
                        st.session_state.messages[i]["feedback_sent"] = True
                        st.rerun()
                with fb_col2:
                    if st.button("👎", key=f"neg_{i}"):
                        _post_feedback(msg.get("question", ""), "negative")
                        st.session_state.messages[i]["feedback_sent"] = True
                        st.rerun()

    # Input del usuario
    if question := st.chat_input("Escribe tu pregunta…"):
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Llamar al agente
        with st.chat_message("assistant"):
            with st.spinner("El agente está pensando…"):
                result = _query_agent(question)

            if result:
                answer = result.get("answer", "Sin respuesta.")
                sources = result.get("sources", [])
                model = result.get("model", "")
                elapsed = result.get("response_time_ms", 0)

                st.markdown(answer)
                _render_sources(sources)
                st.caption(f"Modelo: `{model}` · {elapsed} ms")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "question": question,
                    "feedback_sent": False,
                })
            else:
                fallback = "No pude obtener una respuesta. Verifica que la API esté corriendo."
                st.markdown(fallback)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": fallback,
                    "sources": [],
                    "question": question,
                    "feedback_sent": True,
                })

    # Botón para limpiar el historial
    if st.session_state.messages:
        if st.button("🗑️ Limpiar conversación", use_container_width=False):
            st.session_state.messages = []
            st.rerun()
