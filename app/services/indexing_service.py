import hashlib

from app.config import settings
from app.models.chunk import IndexedChunkRecord, IndexingSummary
from app.models.document import DocumentChunk
from app.services.embedding_provider import GeminiEmbeddingProvider
from app.services.vector_repository import ChromaVectorRepository


def _document_id(filename: str) -> str:
    """Genera un ID determinístico para un documento a partir del nombre."""
    return hashlib.md5(filename.encode()).hexdigest()


def _chunk_id(document_id: str, chunk_index: int) -> str:
    return f"{document_id}_{chunk_index}"


class IndexingService:
    """
    Orquesta la indexación vectorial:
      chunks → embeddings (Gemini) → Chroma
    """

    def __init__(
        self,
        embedding_provider: GeminiEmbeddingProvider | None = None,
        vector_repo: ChromaVectorRepository | None = None,
    ):
        self.embedder = embedding_provider or GeminiEmbeddingProvider(
            api_key=settings.gemini_api_key
        )
        self.repo = vector_repo or ChromaVectorRepository(
            path=settings.chroma_path
        )

    def index(self, chunks: list[DocumentChunk], filename: str) -> IndexingSummary:
        """
        Indexa una lista de chunks en Chroma.
        Si el documento ya existía, reemplaza sus chunks anteriores.

        Args:
            chunks: lista de DocumentChunk del módulo de ingesta
            filename: nombre del archivo (usado como clave del documento)

        Returns:
            IndexingSummary con el resumen de la operación
        """
        document_id = _document_id(filename)

        # 1. Eliminar indexación anterior si existe
        self.repo.delete_by_document(document_id)

        if not chunks:
            return IndexingSummary(
                document_id=document_id,
                source_filename=filename,
                indexed_chunks=0,
                embedding_model=self.embedder.model_name(),
            )

        # 2. Generar embeddings en batch
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # 3. Construir IndexedChunkRecord
        records = [
            IndexedChunkRecord(
                chunk_id=_chunk_id(document_id, chunk.chunk_index),
                document_id=document_id,
                source_filename=chunk.source_filename,
                document_type=chunk.document_type,
                content=chunk.content,
                embedding=embeddings[i],
                embedding_model=self.embedder.model_name(),
                chunk_index=chunk.chunk_index,
                total_chunks=chunk.total_chunks,
                author=chunk.author,
                created_at=chunk.created_at,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                slide_number=chunk.slide_number,
            )
            for i, chunk in enumerate(chunks)
        ]

        # 4. Guardar en Chroma
        self.repo.upsert_chunks(records)

        return IndexingSummary(
            document_id=document_id,
            source_filename=filename,
            indexed_chunks=len(records),
            embedding_model=self.embedder.model_name(),
        )
