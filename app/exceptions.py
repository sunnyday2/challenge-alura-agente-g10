class UnsupportedFormatException(Exception):
    """Se lanza cuando el formato del archivo no está soportado."""

    def __init__(self, filename: str, extension: str):
        self.filename = filename
        self.extension = extension
        super().__init__(
            f"Formato no soportado: '{extension}' en archivo '{filename}'. "
            f"Formatos aceptados: pdf, docx, xlsx, pptx, md, csv, json, html, txt"
        )


class DocumentParseException(Exception):
    """Se lanza cuando ocurre un error al extraer texto de un documento."""

    def __init__(self, filename: str, reason: str):
        self.filename = filename
        self.reason = reason
        super().__init__(f"Error al procesar '{filename}': {reason}")


class RetrievalException(Exception):
    """Se lanza cuando falla la búsqueda semántica en el vector store."""
    pass


class LLMException(Exception):
    """Se lanza cuando falla la llamada al LLM (Gemini)."""
    pass
