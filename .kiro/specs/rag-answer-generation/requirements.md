# Requisitos — Generación de Respuestas RAG

## ¿Qué hace este módulo?
Recibe la pregunta del usuario y el contexto recuperado, construye el prompt, llama a **Google Gemini Flash**, valida la respuesta y la devuelve con las citas de fuente.
Si no hay suficiente evidencia, devuelve una respuesta segura en lugar de inventar información.

## Requisitos

### 1. Respuesta fundamentada en los documentos
- El prompt le indica a Gemini que responda **solo** con información del contexto proporcionado.
- No se permite al modelo usar conocimiento externo.
- Si no hay contexto suficiente, no se intenta generar una respuesta — se activa el fallback.

### 2. Citas de fuente
- Cada respuesta incluye referencias de los chunks usados.
- Las citas incluyen: nombre del archivo, sección, número de página o slide (cuando están disponibles).
- No se inventan campos que no existen en los metadatos.

### 3. Control de alucinaciones
- Si no hay chunks recuperados o los scores son muy bajos → fallback.
- Si la respuesta generada indica que no hay información → registrar como fallback.

### 4. Respuesta de fallback
- Cuando no hay evidencia suficiente, la respuesta dice claramente que la información no se encontró.
- El fallback no incluye citas inventadas.

### 5. Respuesta estructurada
- La respuesta siempre tiene: texto, lista de citas, flag de fallback y motivo.
- El `model_name` en la respuesta siempre es `"gemini-2.5-flash"`.

### 6. Integración con la API
- El endpoint `POST /api/v1/chat/query` ejecuta retrieval + generación en un solo paso.
- La `GEMINI_API_KEY` se lee del `.env` — misma key que para embeddings.
- Si Gemini devuelve error 429 (rate limit), se responde con un mensaje claro al usuario.
