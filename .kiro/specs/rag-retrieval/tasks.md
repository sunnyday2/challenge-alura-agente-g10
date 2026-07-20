# Tareas — Recuperación RAG (Retrieval)

- [ ] 1. Crear modelos `RetrievedChunk` y `RetrievalResponse` en `app/models/`

- [ ] 2. Agregar `embed_query()` al `EmbeddingProvider`
  - Reutilizar la implementación del módulo de indexación
  - Verificar que el modelo sea el mismo que se usó para indexar

- [ ] 3. Agregar métodos de búsqueda al `VectorRepository`
  - [ ] 3.1 `search_similar(vector, top_k, filters)` — búsqueda semántica
  - [ ] 3.2 Soporte de filtros por category, filename y rango de fechas
  - [ ] 3.3 Retornar chunks con texto, score y metadatos

- [ ] 4. Implementar `Reranker` (opcional pero recomendado)
  - [ ] 4.1 `rerank(question, candidates)` → lista reordenada
  - [ ] 4.2 Fallback al orden de similitud vectorial si no está disponible

- [ ] 5. Implementar `ContextAssembler`
  - [ ] 5.1 Construir el bloque de texto con labels de fuente
  - [ ] 5.2 Formato: `[Documento: ... | Sección: ... | Página: ...]`
  - [ ] 5.3 Reducir chunks redundantes cuando sea posible

- [ ] 6. Implementar `RetrievalService`
  - [ ] 6.1 Recibir pregunta + filtros opcionales
  - [ ] 6.2 Generar embedding de la pregunta
  - [ ] 6.3 Buscar chunks candidatos
  - [ ] 6.4 Aplicar filtros y rerankear
  - [ ] 6.5 Ensamblar el contexto
  - [ ] 6.6 Devolver `RetrievalResponse`

- [ ] 7. Conectar con el endpoint `POST /api/v1/chat/query`
  - El retrieval alimenta directamente al módulo de generación de respuestas

- [ ] 8. Escribir tests básicos
  - [ ] 8.1 Test de búsqueda semántica (con mock del vector store)
  - [ ] 8.2 Test de filtros de metadatos
  - [ ] 8.3 Test del context assembler
  - [ ] 8.4 Test del flujo completo de retrieval
