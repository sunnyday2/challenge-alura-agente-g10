import io

import openpyxl

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class XlsxParser(AbstractDocumentParser):
    """Extrae texto de archivos .xlsx — cada hoja se convierte en un bloque."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".xlsx", ".xls"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo abrir el XLSX: {e}")

        blocks: list[ExtractedBlock] = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows_text: list[str] = []

            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c is not None and str(c).strip()]
                if cells:
                    rows_text.append(" | ".join(cells))

            if rows_text:
                blocks.append(
                    ExtractedBlock(
                        content="\n".join(rows_text),
                        section_title=sheet_name,
                    )
                )

        wb.close()
        return ExtractionResult(blocks=blocks)
