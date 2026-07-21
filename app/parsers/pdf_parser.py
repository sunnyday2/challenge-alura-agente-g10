import io
from typing import Optional

import fitz  # PyMuPDF

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class PdfParser(AbstractDocumentParser):
    """Extrae texto de PDFs página por página. Detecta páginas sin texto extraíble."""

    _MIN_CHARS_PER_PAGE = 10

    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo abrir el PDF: {e}")

        blocks: list[ExtractedBlock] = []
        ocr_required = False
        author: Optional[str] = None
        created_at: Optional[str] = None

        metadata = doc.metadata
        if metadata:
            author = metadata.get("author") or None
            created_at = metadata.get("creationDate") or None

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if not text or len(text.strip()) < self._MIN_CHARS_PER_PAGE:
                ocr_required = True
                continue
            blocks.append(ExtractedBlock(content=text, page_number=page_num))

        doc.close()

        return ExtractionResult(
            blocks=blocks,
            author=author,
            created_at=created_at,
            ocr_required=ocr_required,
        )
