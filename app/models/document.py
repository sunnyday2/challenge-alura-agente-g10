from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentChunk:
    """Fragmento de texto extraído de un documento, con metadatos de origen."""

    source_filename: str
    document_type: str
    chunk_index: int
    total_chunks: int
    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    slide_number: Optional[int] = None
    author: Optional[str] = None
    created_at: Optional[str] = None

    def metadata_dict(self) -> dict:
        """Devuelve los metadatos como dict (útil para Chroma)."""
        return {
            "source_filename": self.source_filename,
            "document_type": self.document_type,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "page_number": self.page_number,
            "section_title": self.section_title or "",
            "slide_number": self.slide_number,
            "author": self.author or "",
            "created_at": self.created_at or "",
        }


@dataclass
class ParsedDocument:
    """Resultado del pipeline de ingesta: texto extraído + chunks listos para indexar."""

    source_filename: str
    document_type: str
    raw_text_length: int
    cleaned_text_length: int
    ocr_required: bool
    chunks: list[DocumentChunk] = field(default_factory=list)
    author: Optional[str] = None
    created_at: Optional[str] = None

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)
