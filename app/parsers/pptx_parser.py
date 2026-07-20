import io

from pptx import Presentation

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class PptxParser(AbstractDocumentParser):
    """Extrae texto de archivos .pptx — cada diapositiva es un bloque."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".pptx", ".ppt"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            prs = Presentation(io.BytesIO(content))
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo abrir el PPTX: {e}")

        blocks: list[ExtractedBlock] = []

        for slide_num, slide in enumerate(prs.slides, start=1):
            texts: list[str] = []
            slide_title: str | None = None

            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for para in shape.text_frame.paragraphs:
                    text = "".join(run.text for run in para.runs).strip()
                    if text:
                        texts.append(text)

            # Primer texto largo suele ser el título
            if texts:
                slide_title = texts[0] if len(texts[0]) < 120 else None

            if texts:
                blocks.append(
                    ExtractedBlock(
                        content="\n".join(texts),
                        slide_number=slide_num,
                        section_title=slide_title,
                    )
                )

        return ExtractionResult(blocks=blocks)
