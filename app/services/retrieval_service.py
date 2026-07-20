import os

import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.exceptions import RetrievalException
from app.models.chunk import Chunk


class RetrievalService:
    """
    Búsqueda semántica en Chroma.
    Convierte la pregunta en embedding y devuelve los chunks más similares.
    """

    def __init__(self) -> None:
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=f"models/{settings.gemini_embedding_model}",
            google_api_key=settings.gemini_api_key,
        )
        os.makedirs(settings.chroma_path, exist_ok=True)
        self._chroma = chromadb.PersistentClient(path=settings.chroma_path)
        self._collection = self._chroma.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def retrieve(self, question: str, top_k: int | None = None) -> list[Chunk]:
        """
        Busca los chunks más relevantes para la pregunta.

        Args:
            question: texto de la pregunta del usuario.
            top_k: número de resultados; usa settings.retrieval_top_k por defecto.

        Returns:
            Lista de Chunk ordenados por relevancia.

        Raises:
            RetrievalException: si falla la búsqueda.
        """
        k = top_k or settings.retrieval_top_k

        try:
            query_embedding = self._embeddings.embed_query(question)
        except Exception as e:
            raise RetrievalException(f"Error generando embedding de la pregunta: {e}")

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, self._collection.count() or 1),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise RetrievalException(f"Error consultando el vector store: {e}")

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        chunks: list[Chunk] = []
        for doc_text, meta in zip(documents, metadatas):
            chunk = Chunk(
                id=f"{meta.get('source_filename', '')}_{meta.get('chunk_index', 0)}",
                content=doc_text,
                source_filename=meta.get("source_filename", ""),
                document_type=meta.get("document_type", ""),
                chunk_index=meta.get("chunk_index", 0),
                total_chunks=meta.get("total_chunks", 0),
                page_number=meta.get("page_number") or None,
                section_title=meta.get("section_title") or None,
                slide_number=meta.get("slide_number") or None,
            )
            chunks.append(chunk)

        return chunks
