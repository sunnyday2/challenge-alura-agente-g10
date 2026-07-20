# Tareas — Generación de Respuestas RAG

- [ ] 1. Crear modelos `Citation` y `AnswerResponse` en `app/schemas/`

- [ ] 2. Implementar `GeminiLLMProvider`
  - [ ] 2.1 Configurar `google-genai` con `GEMINI_API_KEY` del `.env`
  - [ ] 2.2 Implementar `generate(prompt)` usando `gemini-2.5-flash`
  - [ ] 2.3 Manejo de error 429 (rate limit) con mensaje claro al usuario
  - [ ] 2.4 Agregar `GEMINI_MODEL_ID` a `config.py` con valor por defecto `"gemini-2.5-flash"`

- [ ] 3. Implementar `PromptBuilder`
  - [ ] 3.1 Instrucción de grounding: "respondé SOLO con el contexto"
  - [ ] 3.2 Incluir el contexto con labels `[Documento: ... | Sección: ... | Página: ...]`
  - [ ] 3.3 Instrucción explícita de responder en el idioma de la pregunta

- [ ] 4. Implementar `AnswerValidator`
  - [ ] 4.1 Fallback si no hay chunks recuperados
  - [ ] 4.2 Fallback si todos los similarity scores están por debajo del umbral
  - [ ] 4.3 Detectar si la respuesta contiene la frase de "no encontré"

- [ ] 5. Implementar `CitationFormatter`
  - [ ] 5.1 Construir citas desde los metadatos de los chunks usados
  - [ ] 5.2 Solo incluir campos que existen (sin inventar)

- [ ] 6. Implementar `FallbackPolicy`
  - [ ] 6.1 Devolver respuesta clara de "no encontrado"
  - [ ] 6.2 Incluir `fallback_reason`: `"no_context"` o `"low_confidence"`
  - [ ] 6.3 Sin citas en el fallback

- [ ] 7. Implementar `AnswerGenerationService`
  - [ ] 7.1 Recibir pregunta + chunks del retrieval
  - [ ] 7.2 Construir prompt con `PromptBuilder`
  - [ ] 7.3 Llamar a `GeminiLLMProvider`
  - [ ] 7.4 Validar con `AnswerValidator`
  - [ ] 7.5 Formatear citas o activar fallback
  - [ ] 7.6 Devolver `AnswerResponse`

- [ ] 8. Conectar con `POST /api/v1/chat/query`
  - El endpoint orquesta: retrieval → generación → respuesta final

- [ ] 9. Escribir tests básicos
  - [ ] 9.1 Test del `PromptBuilder` (verificar que el contexto está incluido)
  - [ ] 9.2 Test del `CitationFormatter`
  - [ ] 9.3 Test del `FallbackPolicy` (cuándo se activa)
  - [ ] 9.4 Test del flujo completo (con mock de `GeminiLLMProvider`)
