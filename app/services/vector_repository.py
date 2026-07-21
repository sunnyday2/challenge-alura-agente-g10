from app.models.chunk import IndexedChunkRecord
from app.exceptions import RetrievalException


class ChromaVectorRepository:
    """Persiste y consulta vectores en Chroma (local en disco)."""

    COLLECTION = "documents"

    def __init__(self, path: str):
        import chromadb  # import lazy — permite mockear en tests
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, records: list[IndexedChunkRecord]) -> None:
        """Guarda o actualiza los chunks en Chroma."""
        if not records:
            return
        try:
            self.collection.upsert(
                ids=[r.chunk_id for r in records],
                embeddings=[r.embedding for r in records],
                documents=[r.content for r in records],
                metadatas=[r.metadata_dict() for r in records],
            )
        except Exception as e:
            raise RetrievalException(f"Error guardando en Chroma: {e}") from e

    def delete_by_document(self, document_id: str) -> None:
        """Elimina todos los chunks de un documento (para reindexación)."""
        try:
            results = self.collection.get(where={"document_id": document_id})
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
        except Exception as e:
            raise RetrievalException(f"Error eliminando documento de Chroma: {e}") from e

    def count_by_document(self, document_id: str) -> int:
        """Cuenta chunks indexados de un documento."""
        try:
            results = self.collection.get(where={"document_id": document_id})
            return len(results["ids"])
        except Exception:
            return 0

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        """Busca los chunks más similares a un embedding."""
        try:
            kwargs: dict = {
                "query_embeddings": [embedding],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where
            results = self.collection.query(**kwargs)
            return [
                {
                    "chunk_id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i, doc_id in enumerate(results["ids"][0])
            ]
        except Exception as e:
            raise RetrievalException(f"Error consultando Chroma: {e}") from e
