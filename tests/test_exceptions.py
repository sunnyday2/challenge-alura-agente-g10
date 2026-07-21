from app.exceptions import (
    DocumentParseException,
    LLMException,
    RetrievalException,
    UnsupportedFormatException,
)


def test_unsupported_format_message() -> None:
    exc = UnsupportedFormatException("video.mp4", ".mp4")
    assert ".mp4" in str(exc)
    assert "video.mp4" in str(exc)
    assert exc.filename == "video.mp4"
    assert exc.extension == ".mp4"


def test_document_parse_exception_message() -> None:
    exc = DocumentParseException("report.pdf", "PDF corrupto")
    assert "report.pdf" in str(exc)
    assert "PDF corrupto" in str(exc)
    assert exc.filename == "report.pdf"
    assert exc.reason == "PDF corrupto"


def test_retrieval_exception_is_exception() -> None:
    exc = RetrievalException("Chroma falló")
    assert isinstance(exc, Exception)
    assert "Chroma falló" in str(exc)


def test_llm_exception_is_exception() -> None:
    exc = LLMException("Ollama no responde")
    assert isinstance(exc, Exception)
    assert "Ollama no responde" in str(exc)
