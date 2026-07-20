import re

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class MarkdownParser(AbstractDocumentParser):
    """Extrae texto de archivos Markdown, agrupando por sección (heading)."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            text = content.decode("utf-8", errors="replace")
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo decodificar el Markdown: {e}")

        blocks: list[ExtractedBlock] = []
        sections = _HEADING_RE.split(text)

        # Si no hay headings, tratar como bloque único
        if len(sections) <= 1:
            if text.strip():
                blocks.append(ExtractedBlock(content=text.strip()))
            return ExtractionResult(blocks=blocks)

        # El split incluye: [texto-antes, nivel, titulo, contenido, nivel, titulo, contenido, ...]
        # Primero el texto antes del primer heading
        if sections[0].strip():
            blocks.append(ExtractedBlock(content=sections[0].strip()))

        it = iter(sections[1:])
        for level_str, title, body in zip(it, it, it):
            body = body.strip()
            if body:
                blocks.append(ExtractedBlock(content=body, section_title=title.strip()))

        return ExtractionResult(blocks=blocks)
