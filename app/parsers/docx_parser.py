from docx import Document

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class DocxParser(AbstractDocumentParser):
    """Extrae texto de archivos .docx párrafo por párrafo."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".docx"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        import io

        try:
            doc = Document(io.BytesIO(content))
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo abrir el DOCX: {e}")

        blocks: list[ExtractedBlock] = []
        current_section: str | None = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Detectar títulos de sección por estilo
            if para.style.name.startswith("Heading"):
                current_section = text

            blocks.append(
                ExtractedBlock(content=text, section_title=current_section)
            )

        # Extraer metadatos del core_properties
        author: str | None = None
        created_at: str | None = None
        try:
            props = doc.core_properties
            author = props.author or None
            if props.created:
                created_at = props.created.isoformat()
        except Exception:
            pass

        return ExtractionResult(blocks=blocks, author=author, created_at=created_at)
