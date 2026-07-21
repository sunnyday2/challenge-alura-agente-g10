import os

from app.exceptions import UnsupportedFormatException
from app.parsers.base_parser import AbstractDocumentParser
from app.parsers.csv_parser import CsvParser
from app.parsers.docx_parser import DocxParser
from app.parsers.html_parser import HtmlParser
from app.parsers.json_parser import JsonParser
from app.parsers.markdown_parser import MarkdownParser
from app.parsers.pdf_parser import PdfParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.txt_parser import TxtParser
from app.parsers.xlsx_parser import XlsxParser

# Registro: extensión → instancia del parser
_PARSERS: list[AbstractDocumentParser] = [
    PdfParser(),
    DocxParser(),
    XlsxParser(),
    PptxParser(),
    MarkdownParser(),
    CsvParser(),
    JsonParser(),
    HtmlParser(),
    TxtParser(),
]

_EXTENSION_MAP: dict[str, AbstractDocumentParser] = {}
for _parser in _PARSERS:
    for _ext in _parser.supported_extensions:
        _EXTENSION_MAP[_ext.lower()] = _parser


def get_parser(filename: str) -> AbstractDocumentParser:
    """
    Devuelve el parser adecuado según la extensión del archivo.

    Raises:
        UnsupportedFormatException: si la extensión no está registrada.
    """
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    parser = _EXTENSION_MAP.get(ext)
    if parser is None:
        raise UnsupportedFormatException(filename, ext)

    return parser


def supported_extensions() -> list[str]:
    """Lista de todas las extensiones soportadas."""
    return sorted(_EXTENSION_MAP.keys())
