# Diseño — Indexación Vectorial

## Flujo general

```
Chunks (del módulo de ingesta)
    → IndexingService
        → GeminiEmbeddingProvider  →  vectores (text-embedding-004)
        → VectorRepository         →  guarda vectores + metadatos en Chroma
    ← resumen de indexación
```

## Componentes

### IndexingService
Orquesta todo:
1. Recibe la lista de chunks
2. Genera embeddings en batch con Gemini text-embedding-004
3. Guarda los vectores con metadatos en Chroma
4. Si es reindexación, elimina los vectores anteriores del mismo documento
5. Devuelve el resumen (chunk count, modelo, etc.)

### GeminiEmbeddingProvider
Llama a la API de Gemini para generar embeddings. Lee la API key desde `.env`.

```python
from google import genai

class GeminiEmbeddingProvider:
    MODEL = "text-embedding-004"

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        result = self.client.models.embed_content(
            model=self.MODEL,
            contents=texts,
            config={"task_type": "RETRIEVAL_DOCUMENT"}
        )
        return [e.values for e in result.embeddings]

    def model_name(self) -> str:
        return self.MODEL
```

### VectorRepository (Chroma)
Persiste los vectores localmente en disco. Sin servidor externo.

```python
import chromadb

class ChromaVectorRepository:
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("documents")

    def upsert_chunks(self, records: list[IndexedChunkRecord]): ...
    def delete_by_document(self, document_id: str): ...
    def count_by_document(self, document_id: str) -> int: ...
```

El path de Chroma viene de la variable de entorno `CHROMA_PATH=./data/chroma_db`.

## Modelo de datos

### IndexedChunkRecord
```python
class IndexedChunkRecord:
    chunk_id: str
    document_id: str
    source_filename: str
    document_type: str
    content: str
    embedding: list[float]
    embedding_model: str      # "text-embedding-004"
    chunk_index: int
    total_chunks: int
    # metadatos opcionales
    category: str | None
    author: str | None
    created_at: str | None
    updated_at: str | None
    page_number: int | None
    section_title: str | None
    slide_number: int | None
```

## Respuesta de la API (indexación exitosa)
```json
{
  "document_id": "doc-123",
  "source_filename": "politica_vacaciones.pdf",
  "indexed_chunks": 18,
  "embedding_model": "text-embedding-004",
  "vector_store": "chroma"
}
```

## Límites del plan gratuito de Gemini
- text-embedding-004: 1.500 req/día, 1 req/seg en free tier
- Para documentos de hasta ~100 chunks esto es más que suficiente
- Si se supera el límite, Gemini devuelve un error 429 que el IndexingService debe manejar con retry
