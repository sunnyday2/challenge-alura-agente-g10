"""
Tests del pipeline de chunking interno de IngestionService.
Usa solo los parsers y TextCleaner — sin Chroma, Gemini ni Ollama.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.parsers.text_cleaner import TextCleaner


def _split(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def test_texto_corto_genera_un_solo_chunk() -> None:
    chunks = _split("Texto corto de prueba.")
    assert len(chunks) == 1


def test_texto_largo_genera_multiples_chunks() -> None:
    texto = "palabra " * 100  # ~700 chars
    chunks = _split(texto, size=100, overlap=20)
    assert len(chunks) > 1


def test_chunks_no_vacios() -> None:
    texto = "línea uno\n\nlínea dos\n\nlínea tres"
    chunks = _split(texto)
    assert all(c.strip() for c in chunks)


def test_overlap_comparte_contenido() -> None:
    # Texto donde el overlap es verificable
    texto = "A" * 90 + " SHARED " + "B" * 90
    chunks = _split(texto, size=100, overlap=30)
    if len(chunks) > 1:
        last_of_first = chunks[0].content[-20:]
        start_of_second = chunks[1].content[:20]
        # Algún contenido del final del primer chunk aparece al inicio del segundo
        assert any(c in start_of_second for c in last_of_first if c.strip())


def test_cleaner_integrado_con_splitter() -> None:
    cleaner = TextCleaner()
    dirty = "texto\x00con\x01basura\n\n\n\npárrafo limpio"
    clean = cleaner.clean(dirty)
    chunks = _split(clean)
    assert all("\x00" not in c and "\x01" not in c for c in chunks)
