from typing import Optional

from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    """Request para hacer una pregunta al agente RAG."""

    question: str = Field(..., min_length=3, max_length=2000)


class SourceReference(BaseModel):
    """Referencia a un fragmento de documento usado en la respuesta."""

    document: str
    section: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None


class ChatQueryResponse(BaseModel):
    """Respuesta del agente RAG con la respuesta y sus fuentes."""

    answer: str
    sources: list[SourceReference]
    model: str
    response_time_ms: int


class FeedbackRequest(BaseModel):
    """Feedback del usuario sobre una respuesta (👍 / 👎)."""

    question: str
    feedback: str = Field(..., pattern="^(positive|negative)$")
