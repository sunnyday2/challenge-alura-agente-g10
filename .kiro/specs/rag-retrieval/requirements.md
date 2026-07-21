# Requisitos — Recuperación RAG (Retrieval)

## ¿Qué hace este módulo?
Recibe la pregunta del usuario, la convierte en embedding, busca los chunks más relevantes en el vector store y arma el contexto que se le va a pasar al LLM.

## Requisitos

### 1. Embedding de la pregunta
- La pregunta se convierte en un vector usando el mismo modelo que se usó para indexar los chunks.
- Si falla la generación del embedding, se devuelve un error claro.

### 2. Búsqueda semántica
- El sistema busca los chunks más similares a la pregunta en el vector store.
- Se recupera un conjunto candidato más grande que el número final de chunks (para poder filtrar y rerankear).
- Los resultados incluyen el texto del chunk y sus metadatos de fuente.
- Si no hay resultados relevantes, se devuelve una respuesta vacía que el siguiente módulo puede manejar.

### 3. Filtros por metadatos (opcional)
- Se puede filtrar por categoría, rango de fechas o nombre de documento.
- Si se proporcionan filtros, se aplican durante o antes de la búsqueda semántica.

### 4. Reranking (opcional)
- Los chunks candidatos se pueden rerankear para mejorar la precisión.
- Si el reranker no está disponible, se usa el orden de similitud vectorial como fallback.
- Los metadatos de fuente se preservan siempre para las citas.

### 5. Armado del contexto
- Los chunks finales se ensamblan en un bloque de contexto listo para el prompt.
- Se incluyen: filename, sección, página/slide y fechas cuando están disponibles.
- Si hay chunks muy similares o duplicados, se reduce la redundancia.

### 6. Integración con la API
- El endpoint devuelve los chunks seleccionados en orden de relevancia y el bloque de contexto listo para el LLM.
- Si falla el retrieval, se devuelve un error legible.
