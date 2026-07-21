"""
Tests del RAGService — usa mocks para Ollama y Chroma.
No requiere servicios externos corriendo.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models.chunk import Chunk
from app.schemas.chat import ChatQueryResponse


def _make_chunk(i: int = 0, filename: str = "doc.pdf") -> Chunk:
    return Chunk(
        id=f"{filename}_{i}",
        content=f"Contenido relevante del fragmento {i}.",
        source_filename=filename,
        document_type="pdf",
        chunk_index=i,
        total_chunks=3,
        page_number=i + 1,
        section_title="Sección de prueba",
    )


@pytest.fixture
def rag_with_mocks():
    """RAGService con RetrievalService y OllamaLLM completamente mockeados."""
    with (
        patch("app.services.rag_service.RetrievalService") as mock_retrieval_cls,
        patch("app.services.rag_service.OllamaLLM") as mock_llm_cls,
    ):
        mock_retrieval = MagicMock()
        mock_retrieval_cls.return_value = mock_retrieval

        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        # Importar después del patch para capturar los mocks
        from app.services.rag_service import RAGService

        service = RAGService()
        yield service, mock_retrieval, mock_llm


def test_query_devuelve_respuesta_con_fuentes(rag_with_mocks) -> None:
    service, mock_retrieval, mock_llm = rag_with_mocks
    mock_retrieval.retrieve.return_value = [_make_chunk(0), _make_chunk(1)]
    mock_llm.invoke.return_value = "Los empleados tienen 15 días de vacaciones."

    response = service.query("¿Cuántos días de vacaciones hay?")

    assert isinstance(response, ChatQueryResponse)
    assert "vacaciones" in response.answer.lower()
    assert len(response.sources) >= 1
    assert response.sources[0].document == "doc.pdf"


def test_query_sin_documentos_usa_fallback(rag_with_mocks) -> None:
    service, mock_retrieval, mock_llm = rag_with_mocks
    mock_retrieval.retrieve.return_value = []

    response = service.query("¿Cuántos días de vacaciones hay?")

    assert isinstance(response, ChatQueryResponse)
    mock_llm.invoke.assert_not_called()
    assert response.sources == []


def test_query_limpia_thinking_tags(rag_with_mocks) -> None:
    service, mock_retrieval, mock_llm = rag_with_mocks
    mock_retrieval.retrieve.return_value = [_make_chunk()]
    mock_llm.invoke.return_value = "<think>Pensando...</think>La respuesta final."

    response = service.query("pregunta")

    assert "<think>" not in response.answer
    assert "La respuesta final." in response.answer


def test_query_deduplica_fuentes(rag_with_mocks) -> None:
    service, mock_retrieval, mock_llm = rag_with_mocks
    # Tres chunks del mismo doc/sección/página → deben deduplicarse a 1 fuente
    chunks = [
        Chunk(f"doc_{i}", "texto", "doc.pdf", "pdf", i, 3,
              page_number=1, section_title="Intro")
        for i in range(3)
    ]
    mock_retrieval.retrieve.return_value = chunks
    mock_llm.invoke.return_value = "Respuesta."

    response = service.query("pregunta")
    assert len(response.sources) == 1


def test_record_feedback_no_lanza_excepcion(rag_with_mocks) -> None:
    service, _, _ = rag_with_mocks
    # No debe lanzar ninguna excepción
    service.record_feedback("¿pregunta?", "positive")
    service.record_feedback("¿pregunta?", "negative")
