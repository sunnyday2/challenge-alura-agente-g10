import pytest

from app.parsers.text_cleaner import TextCleaner


@pytest.fixture
def cleaner() -> TextCleaner:
    return TextCleaner()


def test_clean_empty_string(cleaner: TextCleaner) -> None:
    assert cleaner.clean("") == ""


def test_removes_control_chars(cleaner: TextCleaner) -> None:
    dirty = "hello\x00world\x1f!"
    result = cleaner.clean(dirty)
    assert "\x00" not in result
    assert "\x1f" not in result
    assert "helloworld!" in result


def test_collapses_multiple_spaces(cleaner: TextCleaner) -> None:
    result = cleaner.clean("too   many    spaces")
    assert result == "too many spaces"


def test_normalizes_newlines(cleaner: TextCleaner) -> None:
    result = cleaner.clean("line1\n\n\n\nline2")
    assert result == "line1\n\nline2"


def test_strips_leading_trailing_whitespace(cleaner: TextCleaner) -> None:
    result = cleaner.clean("  trimmed  ")
    assert result == "trimmed"


def test_preserves_single_newlines(cleaner: TextCleaner) -> None:
    result = cleaner.clean("line1\nline2")
    assert result == "line1\nline2"
