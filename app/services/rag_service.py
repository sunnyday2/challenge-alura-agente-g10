import json
import os
import time
from datetime import datetime, timezone
from typing import Optional

from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.exceptions import LLMException, RetrievalException
from app.models.chunk import Chunk
from app.schemas.chat import ChatQueryResponse, SourceReference
from app.services.retrieval_service import RetrievalService

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Eres un asistente de IA que responde preguntas sobre documentos internos de una empresa.
Usa SOLO la información de los fragmentos de contexto proporcionados.
Si la respuesta no está en el contexto, di claramente que no tienes esa información.
Responde de forma clara y concisa. Cita la fuente cuando sea relevante."""

_USER_PROMPT_TEMPLATE = """Contexto de los documentos:
{context}

---
Pregunta: {question}

Responde basándote únicamente en el contexto anterior."""


class RAGService:
    """
    Orquesta el flujo RAG completo:
    pregunta → retrieval → prompt → Qwen3 (Ollama) → respuesta + fuentes.
    También registra cada interacción en el log JSONL.
    """

    def __init__(self) -> None:
        self._retrieval = RetrievalService()
        self._llm = OllamaLLM(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.1,
        )
        #self._llm = ChatGoogleGenerativeAI(
        #    model=settings.gemini_model_id,
        #    temperature=0.7
	#)
        os.makedirs(os.path.dirname(settings.log_path) or ".", exist_ok=True)

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------

    def query(self, question: str) -> ChatQueryResponse:
        """
        Responde una pregunta usando RAG.

        Returns:
            ChatQueryResponse con la respuesta, fuentes y tiempo de respuesta.

        Raises:
            LLMException: si falla la llamada al LLM.
            RetrievalException: si falla la búsqueda semántica.
        """
        start_ms = time.time()

        # 1. Recuperar chunks relevantes
        chunks = self._retrieval.retrieve(question)

        # 2. Construir contexto
        context = self._build_context(chunks)

        # 3. Llamar a Qwen3 via Ollama
        fallback_used = False
        fallback_reason: Optional[str] = None

        if not chunks:
            fallback_used = True
            fallback_reason = "No se encontraron documentos indexados relevantes."
            answer = (
                "No tengo documentos indexados con información sobre esa pregunta. "
                "Por favor sube un documento relacionado primero."
            )
        else:
            prompt = _USER_PROMPT_TEMPLATE.format(context=context, question=question)
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{prompt}"
            try:
                answer = self._llm.invoke(full_prompt)
                # Qwen3 thinking mode puede incluir <think>...</think> — limpiar
                answer = self._strip_thinking_tags(answer)
            except Exception as e:
                raise LLMException(f"Error llamando a Ollama/Qwen3: {e}")

        elapsed_ms = int((time.time() - start_ms) * 1000)

        # 4. Construir referencias de fuentes
        sources = self._build_sources(chunks)

        # 5. Log JSONL
        self._log(
            question=question,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            response_time_ms=elapsed_ms,
        )

        return ChatQueryResponse(
            answer=answer,
            sources=sources,
            model=settings.ollama_model,
            response_time_ms=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # Feedback — actualiza el último registro del log para la pregunta
    # ------------------------------------------------------------------

    def record_feedback(self, question: str, feedback: str) -> None:
        """Escribe una entrada de feedback en el log JSONL."""
        self._log(question=question, feedback=feedback)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _build_context(self, chunks: list[Chunk]) -> str:
        parts: list[str] = []
        for i, chunk in enumerate(chunks, start=1):
            source_info = f"[{i}] {chunk.source_filename}"
            if chunk.section_title:
                source_info += f" — {chunk.section_title}"
            if chunk.page_number:
                source_info += f" (pág. {chunk.page_number})"
            elif chunk.slide_number:
                source_info += f" (diap. {chunk.slide_number})"
            parts.append(f"{source_info}\n{chunk.content}")
        return "\n\n---\n\n".join(parts)

    def _build_sources(self, chunks: list[Chunk]) -> list[SourceReference]:
        seen: set[str] = set()
        sources: list[SourceReference] = []
        for chunk in chunks:
            key = f"{chunk.source_filename}|{chunk.section_title}|{chunk.page_number}"
            if key not in seen:
                seen.add(key)
                sources.append(
                    SourceReference(
                        document=chunk.source_filename,
                        section=chunk.section_title or None,
                        page=chunk.page_number or None,
                        slide=chunk.slide_number or None,
                    )
                )
        return sources

    def _strip_thinking_tags(self, text: str) -> str:
        """Elimina bloques <think>...</think> que Qwen3 genera en modo thinking."""
        import re
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    def _log(
        self,
        question: str,
        fallback_used: bool = False,
        fallback_reason: Optional[str] = None,
        response_time_ms: int = 0,
        feedback: Optional[str] = None,
    ) -> None:
        """Escribe una línea JSONL en el archivo de log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "response_time_ms": response_time_ms,
            "model": settings.ollama_model,
            "feedback": feedback,
        }
        try:
            with open(settings.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # El log no debe romper la respuesta al usuario
