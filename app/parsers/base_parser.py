from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExtractedBlock:
    """Unidad mínima de texto extraído con su ubicación en el documento."""

    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    slide_number: Optional[int] = None


@dataclass
class ExtractionResult:
    """Resultado completo de un parser: lista de bloques + metadatos del archivo."""

    blocks: list[ExtractedBlock] = field(default_factory=list)
    author: Optional[str] = None
    created_at: Optional[str] = None
    ocr_required: bool = False

    @property
    def full_text(self) -> str:
        """Texto plano completo uniendo todos los bloques."""
        return "\n\n".join(b.content for b in self.blocks if b.content.strip())


class AbstractDocumentParser(ABC):
    """Contrato común que deben implementar todos los parsers de formato."""

    @abstractmethod
    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        """
        Extrae texto e información estructural del archivo.

        Args:
            content: bytes del archivo
            filename: nombre original (usado para mensajes de error)

        Returns:
            ExtractionResult con la lista de bloques y metadatos del archivo
        """
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Lista de extensiones que maneja este parser (ej: ['.pdf'])."""
        ...
