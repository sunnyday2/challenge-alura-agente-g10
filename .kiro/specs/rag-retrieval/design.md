# Diseño — Recuperación RAG (Retrieval)

## Flujo general

```
Pregunta del usuario
    → RetrievalService
        → EmbeddingProvider  →  vector de la pregunta
        → VectorRepository   →  chunks candidatos (con filtros opcionales)
        → Reranker (opcional) →  chunks reordenados por relevancia
        → ContextAssembler   →  bloque de contexto para el LLM
    ← chunks finales + contexto
```

## Componentes

### RetrievalService
Orquesta el retrieval completo:
1. Genera el embedding de la pregunta (mismo modelo que indexación)
2. Busca chunks candidatos en el vector store
3. Aplica filtros de metadatos si los hay
4. Rerankea si está habilitado
5. Selecciona el top-k final
6. Arma el bloque de contexto
7. Devuelve los chunks + contexto

### EmbeddingProvider
El mismo que en indexación — `embed_query(text)` devuelve el vector de la pregunta.
Reutiliza la misma interfaz definida en el módulo de vector-indexing.

### VectorRepository
Métodos de búsqueda:
- `search_similar(vector, top_k, filters)` — búsqueda semántica con filtros opcionales
- Devuelve chunks con texto, score de similitud y metadatos

### Reranker (opcional)
Toma la pregunta y los chunks candidatos, devuelve una lista reordenada por relevancia real.
Si no está disponible, se usa el orden de similitud vectorial.

### ContextAssembler
Arma el bloque de texto que se le pasa al LLM:
```
[Documento: manual_empleados.pdf | Sección: Vacaciones | Página: 12]
Los empleados pueden solicitar vacaciones desde el portal de RRHH...

[Documento: reglamento_interno.pdf | Sección: Beneficios]
El período mínimo de vacaciones es de 5 días hábiles consecutivos...
```

## Modelos de datos

### RetrievedChunk
```python
class RetrievedChunk:
    chunk_id: str
    source_filename: str
    document_type: str
    content: str
    similarity_score: float
    rerank_score: float | None
    section_title: str | None
    page_number: int | None
    slide_number: int | None
    category: str | None
    updated_at: str | None
```

### RetrievalResponse
```python
class RetrievalResponse:
    question: str
    embedding_model: str
    candidate_count: int   # cuántos chunks se recuperaron antes del reranking
    final_count: int       # cuántos van al LLM
    results: list[RetrievedChunk]
    context_block: str     # texto listo para el prompt
```

## Respuesta de la API
```json
{
  "question": "¿Cuántos días de vacaciones tengo?",
  "embedding_model": "amazon.titan-embed-text-v2",
  "candidate_count": 10,
  "final_count": 4,
  "results": [
    {
      "source_filename": "manual_empleados.pdf",
      "section_title": "Política de Vacaciones",
      "page_number": 12,
      "similarity_score": 0.89,
      "content": "Los empleados tienen 15 días hábiles de vacaciones por año..."
    }
  ],
  "context_block": "[Documento: manual_empleados.pdf | Sección: Política de Vacaciones | Página: 12]\nLos empleados tienen 15 días hábiles de vacaciones por año..."
}
```
