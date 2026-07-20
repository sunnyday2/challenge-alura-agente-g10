import csv
import io

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class CsvParser(AbstractDocumentParser):
    """Convierte un CSV en texto plano legible (encabezado + filas)."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".csv"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            text = content.decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo parsear el CSV: {e}")

        if not rows:
            return ExtractionResult(blocks=[])

        lines: list[str] = []
        for row in rows:
            parts = [f"{k}: {v}" for k, v in row.items() if v and str(v).strip()]
            if parts:
                lines.append(" | ".join(parts))

        block_text = "\n".join(lines)
        return ExtractionResult(
            blocks=[ExtractedBlock(content=block_text)] if block_text else []
        )
