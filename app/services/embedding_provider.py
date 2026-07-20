import time
from typing import Protocol

from app.exceptions import LLMException


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
    def model_name(self) -> str: ...


class GeminiEmbeddingProvider:
    """Genera embeddings con Google Gemini text-embedding-004 via google-genai."""

    MODEL = "text-embedding-004"
    _MAX_RETRIES = 3
    _RETRY_DELAY = 2  # segundos

    def __init__(self, api_key: str):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para una lista de textos (documentos)."""
        return self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        """Genera embedding para una pregunta del usuario."""
        return self._embed([text], task_type="RETRIEVAL_QUERY")[0]

    def model_name(self) -> str:
        return self.MODEL

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        for attempt in range(self._MAX_RETRIES):
            try:
                result = self.client.models.embed_content(
                    model=self.MODEL,
                    contents=texts,
                    config={"task_type": task_type},
                )
                return [e.values for e in result.embeddings]
            except Exception as e:
                err_str = str(e)
                # Rate limit: esperar y reintentar
                if "429" in err_str and attempt < self._MAX_RETRIES - 1:
                    time.sleep(self._RETRY_DELAY * (attempt + 1))
                    continue
                raise LLMException(f"Error generando embeddings ({self.MODEL}): {e}") from e
        raise LLMException("Se agotaron los reintentos para generar embeddings.")
