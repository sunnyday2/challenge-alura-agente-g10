"""
Tests del RetrievalService — mockeando Chroma y Gemini embeddings.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models.chunk import Chunk


@pytest.fixture
def retrieval_with_mocks():
    """RetrievalService con chromadb y GoogleGenerativeAIEmbeddings mockeados."""
    with (
        patch("app.services.retrieval_service.chromadb") as mock_chromadb,
        patch("app.services.retrieval_service.GoogleGenerativeAIEmbeddings") as mock_emb_cls,
    ):
        mock_emb = MagicMock()
        mock_emb_cls.return_value = mock_emb

        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        from app.services.retrieval_service import RetrievalService

        service = RetrievalService()
        service._collection = mock_collection
        service._embeddings = mock_emb
        yield service, mock_emb, mock_collection


def _fake_query_result(n: int = 2):
    """Resultado simulado de chroma.collection.query()."""
    docs = [f"Texto del chunk {i}" for i in range(n)]
    metas = [
        {
            "source_filename": "doc.pdf",
            "document_type": "pdf",
            "chunk_index": i,
            "total_chunks": n,
            "page_number": i + 1,
            "section_title": "Sección",
            "slide_number": 0,
        }
        for i in range(n)
    ]
    return {"documents": [docs], "metadatas": [metas], "distances": [[0.1] * n]}


def test_retrieve_devuelve_chunks(retrieval_with_mocks) -> None:
    service, mock_emb, mock_collection = retrieval_with_mocks
    mock_emb.embed_query.return_value = [0.1] * 768
    mock_collection.count.return_value = 5
    mock_collection.query.return_value = _fake_query_result(2)

    chunks = service.retrieve("¿Cuántos empleados hay?")

    assert len(chunks) == 2
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].source_filename == "doc.pdf"


def test_retrieve_llama_a_embed_query(retrieval_with_mocks) -> None:
    service, mock_emb, mock_collection = retrieval_with_mocks
    mock_emb.embed_query.return_value = [0.1] * 768
    mock_collection.count.return_value = 3
    mock_collection.query.return_value = _fake_query_result(1)

    service.retrieve("pregunta de prueba")

    mock_emb.embed_query.assert_called_once_with("pregunta de prueba")


def test_retrieve_sin_resultados_devuelve_lista_vacia(retrieval_with_mocks) -> None:
    service, mock_emb, mock_collection = retrieval_with_mocks
    mock_emb.embed_query.return_value = [0.1] * 768
    mock_collection.count.return_value = 0
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    chunks = service.retrieve("pregunta")

    assert chunks == []


def test_retrieve_lanza_excepcion_si_falla_embedding(retrieval_with_mocks) -> None:
    from app.exceptions import RetrievalException

    service, mock_emb, _ = retrieval_with_mocks
    mock_emb.embed_query.side_effect = Exception("Gemini caído")

    with pytest.raises(RetrievalException):
        service.retrieve("pregunta")
