from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    """Fragmento de texto listo para ser indexado en el vector store."""

    id: str                        # identificador único: "{filename}_{index}"
    content: str                   # texto del fragmento
    source_filename: str
    document_type: str
    chunk_index: int
    total_chunks: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    slide_number: Optional[int] = None

    def to_metadata(self) -> dict:
        """Convierte los metadatos a dict plano para Chroma."""
        return {
            "source_filename": self.source_filename,
            "document_type": self.document_type,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "page_number": self.page_number or 0,
            "section_title": self.section_title or "",
            "slide_number": self.slide_number or 0,
        }
