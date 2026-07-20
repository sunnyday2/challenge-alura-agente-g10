# Tareas — Indexación Vectorial

- [ ] 1. Crear el modelo `IndexedChunkRecord` en `app/models/`
  - Incluir: chunk_id, document_id, filename, tipo, contenido, embedding, modelo, metadatos opcionales

- [ ] 2. Implementar `GeminiEmbeddingProvider`
  - [ ] 2.1 Configurar `google-genai` con `GEMINI_API_KEY` del `.env`
  - [ ] 2.2 Implementar `embed_texts(texts)` usando `text-embedding-004` con `task_type="RETRIEVAL_DOCUMENT"`
  - [ ] 2.3 Implementar `embed_query(text)` con `task_type="retrieval_query"` (para preguntas)
  - [ ] 2.4 Manejo de error 429 (rate limit) con retry simple

- [ ] 3. Implementar `ChromaVectorRepository`
  - [ ] 3.1 Usar `chromadb.PersistentClient(path=CHROMA_PATH)`
  - [ ] 3.2 Implementar `upsert_chunks(records)` — guarda vectores + metadatos
  - [ ] 3.3 Implementar `delete_by_document(document_id)` — para reindexación
  - [ ] 3.4 Implementar `count_by_document(document_id)`

- [ ] 4. Implementar `IndexingService`
  - [ ] 4.1 Recibir lista de chunks del módulo de ingesta
  - [ ] 4.2 Generar embeddings en batch con `GeminiEmbeddingProvider`
  - [ ] 4.3 Construir los `IndexedChunkRecord`
  - [ ] 4.4 Guardar en Chroma (upsert)
  - [ ] 4.5 Eliminar chunks anteriores si es reindexación
  - [ ] 4.6 Devolver resumen: document_id, chunk count, modelo, vector store

- [ ] 5. Agregar `GEMINI_API_KEY` y `CHROMA_PATH` a `config.py` y `.env.example`

- [ ] 6. Integrar indexación después del upload
  - Pipeline: upload → parse → chunk → **index** → respuesta con resumen

- [ ] 7. Escribir tests básicos
  - [ ] 7.1 Test del `GeminiEmbeddingProvider` (con mock de la API)
  - [ ] 7.2 Test del `ChromaVectorRepository` (upsert y delete)
  - [ ] 7.3 Test del `IndexingService` (flujo completo con mocks)
