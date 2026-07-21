from dataclasses import dataclass
from typing import Optional


@dataclass
class RetrievedChunk:
    """Chunk recuperado del vector store con score de similitud."""
    chunk_id: str
    source_filename: str
    document_type: str
    content: str
    similarity_score: float
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    category: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class RetrievalResult:
    """Resultado completo del retrieval: chunks + contexto ensamblado."""
    question: str
    embedding_model: str
    candidate_count: int
    final_count: int
    chunks: list[RetrievedChunk]
    context_block: str
