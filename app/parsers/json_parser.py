import json

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class JsonParser(AbstractDocumentParser):
    """Serializa JSON como texto legible para indexación."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".json"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            text = content.decode("utf-8", errors="replace")
            data = json.loads(text)
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo parsear el JSON: {e}")

        # Serializar de vuelta de forma legible para el LLM
        readable = json.dumps(data, ensure_ascii=False, indent=2)
        return ExtractionResult(blocks=[ExtractedBlock(content=readable)])
