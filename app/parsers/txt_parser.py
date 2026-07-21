from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class TxtParser(AbstractDocumentParser):
    """Extrae texto de archivos de texto plano (.txt)."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".txt", ".text"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            text = content.decode("utf-8", errors="replace").strip()
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo leer el archivo de texto: {e}")

        if not text:
            return ExtractionResult(blocks=[])

        return ExtractionResult(blocks=[ExtractedBlock(content=text)])
