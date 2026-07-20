import pytest

from app.exceptions import UnsupportedFormatException
from app.parsers.csv_parser import CsvParser
from app.parsers.docx_parser import DocxParser
from app.parsers.html_parser import HtmlParser
from app.parsers.json_parser import JsonParser
from app.parsers.markdown_parser import MarkdownParser
from app.parsers.parser_factory import get_parser, supported_extensions
from app.parsers.pdf_parser import PdfParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.txt_parser import TxtParser
from app.parsers.xlsx_parser import XlsxParser


@pytest.mark.parametrize("filename,expected_class", [
    ("report.pdf", PdfParser),
    ("doc.docx", DocxParser),
    ("sheet.xlsx", XlsxParser),
    ("slides.pptx", PptxParser),
    ("README.md", MarkdownParser),
    ("data.csv", CsvParser),
    ("config.json", JsonParser),
    ("page.html", HtmlParser),
    ("notes.txt", TxtParser),
    ("UPPER.PDF", PdfParser),         # case-insensitive
    ("archive.MD", MarkdownParser),   # case-insensitive
])
def test_get_parser_returns_correct_type(filename: str, expected_class: type) -> None:
    parser = get_parser(filename)
    assert isinstance(parser, expected_class)


def test_get_parser_raises_for_unsupported_format() -> None:
    with pytest.raises(UnsupportedFormatException):
        get_parser("video.mp4")


def test_get_parser_raises_for_no_extension() -> None:
    with pytest.raises(UnsupportedFormatException):
        get_parser("nodotfile")


def test_supported_extensions_returns_list() -> None:
    exts = supported_extensions()
    assert isinstance(exts, list)
    assert ".pdf" in exts
    assert ".docx" in exts
    assert len(exts) >= 9
