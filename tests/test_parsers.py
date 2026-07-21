"""
Tests de parsers usando contenido sintético en memoria — sin disco, sin I/O real.
"""
import csv
import io
import json as _json

import pytest

from app.parsers.csv_parser import CsvParser
from app.parsers.html_parser import HtmlParser
from app.parsers.json_parser import JsonParser
from app.parsers.markdown_parser import MarkdownParser
from app.parsers.txt_parser import TxtParser


# ---------------------------------------------------------------------------
# TxtParser
# ---------------------------------------------------------------------------

class TestTxtParser:
    def setup_method(self) -> None:
        self.parser = TxtParser()

    def test_supported_extensions(self) -> None:
        assert ".txt" in self.parser.supported_extensions

    def test_extracts_plain_text(self) -> None:
        content = b"Hello, world!"
        result = self.parser.parse(content, "test.txt")
        assert len(result.blocks) == 1
        assert result.blocks[0].content == "Hello, world!"

    def test_empty_file_returns_no_blocks(self) -> None:
        result = self.parser.parse(b"", "empty.txt")
        assert result.blocks == []

    def test_whitespace_only_returns_no_blocks(self) -> None:
        result = self.parser.parse(b"   \n   ", "blank.txt")
        assert result.blocks == []


# ---------------------------------------------------------------------------
# MarkdownParser
# ---------------------------------------------------------------------------

class TestMarkdownParser:
    def setup_method(self) -> None:
        self.parser = MarkdownParser()

    def test_supported_extensions(self) -> None:
        assert ".md" in self.parser.supported_extensions

    def test_parses_headings_as_section_titles(self) -> None:
        md = b"# Introduction\n\nSome text here.\n\n## Details\n\nMore details."
        result = self.parser.parse(md, "doc.md")
        assert any(b.section_title == "Introduction" for b in result.blocks)
        assert any(b.section_title == "Details" for b in result.blocks)

    def test_no_headings_returns_single_block(self) -> None:
        md = b"Just plain text without any headings."
        result = self.parser.parse(md, "plain.md")
        assert len(result.blocks) == 1

    def test_empty_markdown_returns_no_blocks(self) -> None:
        result = self.parser.parse(b"", "empty.md")
        assert result.blocks == []


# ---------------------------------------------------------------------------
# CsvParser
# ---------------------------------------------------------------------------

class TestCsvParser:
    def setup_method(self) -> None:
        self.parser = CsvParser()

    def test_supported_extensions(self) -> None:
        assert ".csv" in self.parser.supported_extensions

    def test_parses_csv_rows(self) -> None:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerow({"name": "Alice", "age": "30"})
        writer.writerow({"name": "Bob", "age": "25"})
        content = buf.getvalue().encode()

        result = self.parser.parse(content, "people.csv")
        assert len(result.blocks) == 1
        text = result.blocks[0].content
        assert "Alice" in text
        assert "Bob" in text

    def test_empty_csv_returns_no_blocks(self) -> None:
        result = self.parser.parse(b"", "empty.csv")
        assert result.blocks == []


# ---------------------------------------------------------------------------
# JsonParser
# ---------------------------------------------------------------------------

class TestJsonParser:
    def setup_method(self) -> None:
        self.parser = JsonParser()

    def test_supported_extensions(self) -> None:
        assert ".json" in self.parser.supported_extensions

    def test_parses_json_object(self) -> None:
        data = {"company": "Acme", "employees": 42}
        content = _json.dumps(data).encode()
        result = self.parser.parse(content, "info.json")
        assert len(result.blocks) == 1
        assert "Acme" in result.blocks[0].content

    def test_invalid_json_raises(self) -> None:
        from app.exceptions import DocumentParseException
        with pytest.raises(DocumentParseException):
            self.parser.parse(b"{not valid json", "bad.json")


# ---------------------------------------------------------------------------
# HtmlParser
# ---------------------------------------------------------------------------

class TestHtmlParser:
    def setup_method(self) -> None:
        self.parser = HtmlParser()

    def test_supported_extensions(self) -> None:
        assert ".html" in self.parser.supported_extensions

    def test_strips_script_and_style_tags(self) -> None:
        html = b"""
        <html><head><style>body{color:red}</style></head>
        <body>
          <script>alert('xss')</script>
          <p>Useful content here.</p>
        </body></html>
        """
        result = self.parser.parse(html, "page.html")
        full_text = " ".join(b.content for b in result.blocks)
        assert "alert" not in full_text
        assert "color:red" not in full_text
        assert "Useful content here." in full_text

    def test_extracts_headings_as_section_titles(self) -> None:
        html = b"<html><body><h1>Title</h1><p>Paragraph under title.</p></body></html>"
        result = self.parser.parse(html, "doc.html")
        assert any(b.section_title == "Title" for b in result.blocks)
