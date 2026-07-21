# Tareas — Interfaz, Despliegue y Mantenimiento

## Interfaz

- [ ] 1. Crear `streamlit_app.py` con las secciones básicas
  - [ ] 1.1 Sección de subida de documentos (conectada a `/api/v1/documents/upload`)
  - [ ] 1.2 Sección de chat: input de pregunta, respuesta y citas de fuente
  - [ ] 1.3 Historial de conversación en `st.session_state`
  - [ ] 1.4 Label visible de "Agente de IA"

- [ ] 2. Agregar feedback (👍 / 👎) por respuesta
  - [ ] 2.1 Capturar el evento de feedback
  - [ ] 2.2 Actualizar el registro en el log JSONL

## Configuración

- [ ] 3. Crear `.env.example` con todas las variables
  ```
  GEMINI_API_KEY=
  GEMINI_MODEL_ID=gemini-2.5-flash
  GEMINI_EMBEDDING_MODEL=text-embedding-004
  VECTOR_STORE=chroma
  CHROMA_PATH=./data/chroma_db
  UPLOAD_PATH=./data/uploads
  LOG_PATH=./data/query_log.jsonl
  ```

- [ ] 4. Actualizar `app/config.py` para leer todas las variables con `python-dotenv`

## Despliegue en Oracle Free Tier

- [ ] 5. Crear la VM en OCI Console
  - Shape: VM.Standard.A1.Flex — 2 OCPU, 12 GB RAM
  - OS: Ubuntu 22.04 (imagen ARM)
  - Abrir puertos 22 (SSH), 80 (HTTP), 8000 (API), 8501 (Streamlit) en Security List

- [ ] 6. Instalar Python 3.11, pip, nginx y git en la VM

- [ ] 7. Crear servicio systemd para FastAPI (`/etc/systemd/system/rag-api.service`)
  - Leer el `.env` como `EnvironmentFile`
  - Configurar `Restart=always`

- [ ] 8. Crear servicio systemd para Streamlit (`/etc/systemd/system/rag-ui.service`)
  - Arrancar después de `rag-api.service`

- [ ] 9. Configurar Nginx como reverse proxy
  - `/` → Streamlit (8501) con soporte WebSocket
  - `/api/` → FastAPI (8000)
  - `/docs` → Swagger de FastAPI

## Logging y verificación

- [ ] 10. Implementar logging de preguntas en `app/services/rag_service.py`
  - Guardar en `LOG_PATH` en formato JSONL: timestamp, pregunta, fallback_used, tiempo, feedback

- [ ] 11. Test de humo (smoke test) end-to-end en la VM
  - Subir un documento de prueba
  - Hacer una pregunta y verificar que la respuesta incluye citas
  - Verificar que el log se registra correctamente
