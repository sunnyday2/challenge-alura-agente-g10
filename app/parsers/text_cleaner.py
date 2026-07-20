import re


class TextCleaner:
    """Limpia texto extraído de documentos eliminando ruido sin perder estructura útil."""

    # Caracteres de control excepto \n y \t
    _CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    # Espacios múltiples (sin tocar saltos de línea)
    _MULTI_SPACE = re.compile(r"[ \t]+")
    # Más de 2 saltos de línea consecutivos
    _MULTI_NEWLINE = re.compile(r"\n{3,}")

    def clean(self, text: str) -> str:
        """Aplica todas las reglas de limpieza en secuencia."""
        if not text:
            return ""

        text = self._remove_control_chars(text)
        text = self._normalize_spaces(text)
        text = self._normalize_newlines(text)
        text = text.strip()
        return text

    def _remove_control_chars(self, text: str) -> str:
        """Elimina caracteres de control excepto saltos de línea y tabulaciones."""
        return self._CONTROL_CHARS.sub("", text)

    def _normalize_spaces(self, text: str) -> str:
        """Colapsa espacios y tabs múltiples en uno solo."""
        return self._MULTI_SPACE.sub(" ", text)

    def _normalize_newlines(self, text: str) -> str:
        """Reduce saltos de línea múltiples a máximo dos (preserva separación de párrafos)."""
        # Normalizar \r\n y \r a \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Reducir 3+ saltos a 2
        return self._MULTI_NEWLINE.sub("\n\n", text)
