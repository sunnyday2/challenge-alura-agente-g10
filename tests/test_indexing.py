"""
Tests del modelo Chunk — sin dependencias externas.
Reemplaza el test_indexing.py original que apuntaba a un diseño anterior.
"""
from app.models.chunk import Chunk


def _make_chunk(**kwargs) -> Chunk:
    defaults = dict(
        id="doc.pdf_0",
        content="Contenido de prueba.",
        source_filename="doc.pdf",
        document_type="pdf",
        chunk_index=0,
        total_chunks=3,
    )
    defaults.update(kwargs)
    return Chunk(**defaults)


def test_chunk_id_es_string() -> None:
    chunk = _make_chunk()
    assert isinstance(chunk.id, str)


def test_to_metadata_tiene_campos_obligatorios() -> None:
    chunk = _make_chunk(page_number=5, section_title="Intro")
    meta = chunk.to_metadata()
    assert meta["source_filename"] == "doc.pdf"
    assert meta["document_type"] == "pdf"
    assert meta["chunk_index"] == 0
    assert meta["total_chunks"] == 3
    assert meta["page_number"] == 5
    assert meta["section_title"] == "Intro"


def test_to_metadata_none_values_become_zero_or_empty() -> None:
    chunk = _make_chunk(page_number=None, section_title=None, slide_number=None)
    meta = chunk.to_metadata()
    assert meta["page_number"] == 0
    assert meta["section_title"] == ""
    assert meta["slide_number"] == 0


def test_chunk_indices_son_correctos() -> None:
    chunks = [
        _make_chunk(id=f"doc_{i}", chunk_index=i, total_chunks=5)
        for i in range(5)
    ]
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
        assert chunk.total_chunks == 5
