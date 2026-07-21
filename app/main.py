import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_documents import router as documents_router
from app.api.routes_health import router as health_router
from app.config import settings

# Garantizar que los directorios de datos existen al arrancar
os.makedirs(settings.upload_path, exist_ok=True)
os.makedirs(settings.chroma_path, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_path) or "data", exist_ok=True)

app = FastAPI(
    title="RAG Agent API",
    description=(
        "API de un agente de IA que responde preguntas sobre documentos internos. "
        "Usa RAG con Qwen3 (Ollama) como LLM y Gemini text-embedding-004 para embeddings."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permite llamadas desde Streamlit en desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {
        "message": "RAG Agent API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
