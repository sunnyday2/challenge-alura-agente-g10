"""
Tests de schemas Pydantic — validan que los modelos aceptan y rechazan los inputs correctos.
"""
import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, FeedbackRequest, SourceReference
from app.schemas.document import DocumentListItem, DocumentUploadResponse


# ---------------------------------------------------------------------------
# ChatQueryRequest
# ---------------------------------------------------------------------------

class TestChatQueryRequest:
    def test_valid_question(self) -> None:
        req = ChatQueryRequest(question="¿Cuál es la política de vacaciones?")
        assert req.question == "¿Cuál es la política de vacaciones?"

    def test_question_too_short_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatQueryRequest(question="ab")

    def test_empty_question_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatQueryRequest(question="")


# ---------------------------------------------------------------------------
# FeedbackRequest
# ---------------------------------------------------------------------------

class TestFeedbackRequest:
    def test_positive_feedback(self) -> None:
        req = FeedbackRequest(question="¿Cuántos empleados hay?", feedback="positive")
        assert req.feedback == "positive"

    def test_negative_feedback(self) -> None:
        req = FeedbackRequest(question="¿Cuántos empleados hay?", feedback="negative")
        assert req.feedback == "negative"

    def test_invalid_feedback_value_raises(self) -> None:
        with pytest.raises(ValidationError):
            FeedbackRequest(question="¿Cuántos empleados hay?", feedback="maybe")


# ---------------------------------------------------------------------------
# DocumentUploadResponse
# ---------------------------------------------------------------------------

class TestDocumentUploadResponse:
    def test_default_message(self) -> None:
        resp = DocumentUploadResponse(
            filename="manual.pdf",
            document_type="pdf",
            chunk_count=12,
        )
        assert resp.message == "Documento indexado correctamente."
        assert resp.chunk_count == 12

    def test_custom_message(self) -> None:
        resp = DocumentUploadResponse(
            filename="data.csv",
            document_type="csv",
            chunk_count=3,
            message="Listo.",
        )
        assert resp.message == "Listo."


# ---------------------------------------------------------------------------
# SourceReference
# ---------------------------------------------------------------------------

class TestSourceReference:
    def test_minimal_source(self) -> None:
        src = SourceReference(document="manual.pdf")
        assert src.document == "manual.pdf"
        assert src.page is None
        assert src.section is None

    def test_full_source(self) -> None:
        src = SourceReference(
            document="slides.pptx",
            section="Introducción",
            slide=3,
        )
        assert src.slide == 3
        assert src.section == "Introducción"
