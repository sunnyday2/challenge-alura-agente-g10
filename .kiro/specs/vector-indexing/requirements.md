# Requisitos — Indexación Vectorial

## ¿Qué hace este módulo?
Toma los chunks generados por el módulo de ingesta, genera embeddings para cada uno con Google Gemini y los guarda en Chroma (vector store local en disco).
La salida es una base de conocimiento indexada lista para búsqueda semántica.

## Requisitos

### 1. Generación de embeddings con Gemini
- Cada chunk se convierte en un vector usando `text-embedding-004` de Google Gemini (via `google-genai`).
- La API key se lee desde la variable de entorno `GEMINI_API_KEY` — nunca hardcodeada.
- El mismo modelo se usa para chunks y para preguntas del usuario.
- Si falla la generación (error de red, límite de rate), se devuelve un error claro con posibilidad de retry.

### 2. Persistencia en Chroma (local)
- Los vectores se guardan en Chroma con `PersistentClient` en el path definido por `CHROMA_PATH`.
- Se guarda junto al vector: el texto original del chunk y todos sus metadatos.
- Si se reindexa el mismo documento, se reemplazan los chunks anteriores.

### 3. Metadatos filtrables
- Campos mínimos por chunk: filename, document_type, chunk_index, total_chunks.
- Campos opcionales: category, author, created_at, updated_at, page_number, section_title, slide_number.

### 4. Búsqueda semántica lista
- Chroma está configurado para búsqueda top-k por similitud coseno.
- No se requiere configuración adicional — Chroma lo hace por defecto.

### 5. Integración con la API
- Después de subir y parsear un documento, el sistema lo indexa automáticamente.
- Respuesta exitosa incluye: document_id, chunk count, nombre del modelo de embeddings y vector store.
- En caso de error, respuesta legible con el motivo.
