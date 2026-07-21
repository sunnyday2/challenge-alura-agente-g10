"""
Tests del pipeline de ingesta — solo la capa parser+cleaner+chunking.
No instancia IngestionService real (requiere Chroma+Gemini).
Valida que los parsers producen texto correcto que el cleaner limpia.
"""
import json

import pytest

from app.exceptions import UnsupportedFormatException
from app.parsers.parser_factory import get_parser
from app.parsers.text_cleaner import TextCleaner


def _ingest_text(content: bytes, filename: str) -> str:
    """Simula la capa parser+clean sin Chroma ni embeddings."""
    parser = get_parser(filename)
    result = parser.parse(content, filename)
    cleaner = TextCleaner()
    blocks = [cleaner.clean(b.content) for b in result.blocks]
    return "\n\n".join(b for b in blocks if b)


def test_pipeline_markdown() -> None:
    content = b"# Titulo\n\nContenido del documento.\n\n## Seccion 2\n\nMas texto aqui."
    text = _ingest_text(content, "documento.md")
    assert "Contenido del documento" in text
    assert "Mas texto aqui" in text


def test_pipeline_csv() -> None:
    content = b"nombre,departamento\nAna,IT\nBob,RRHH"
    text = _ingest_text(content, "empleados.csv")
    assert "Ana" in text
    assert "IT" in text


def test_pipeline_json() -> None:
    data = {"empresa": "Alura", "pais": "Brasil", "empleados": 500}
    content = json.dumps(data).encode()
    text = _ingest_text(content, "config.json")
    assert "Alura" in text


def test_pipeline_txt() -> None:
    content = b"Este es un documento de texto simple."
    text = _ingest_text(content, "nota.txt")
    assert "documento de texto" in text


def test_pipeline_html() -> None:
    content = (
        b"<html><body><h1>Manual</h1>"
        b"<p>Politicas de vacaciones.</p></body></html>"
    )
    text = _ingest_text(content, "manual.html")
    assert "vacaciones" in text.lower()


def test_formato_no_soportado_lanza_excepcion() -> None:
    with pytest.raises(UnsupportedFormatException):
        _ingest_text(b"datos", "archivo.xyz")


def test_texto_limpio_no_tiene_caracteres_de_control() -> None:
    content = "Texto\x00con\x01caracteres\x02de\x03control".encode()
    text = _ingest_text(content, "sucio.txt")
    assert "\x00" not in text
    assert "\x01" not in text
