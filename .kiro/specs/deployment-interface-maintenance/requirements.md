# Requisitos — Interfaz, Despliegue y Mantenimiento

## ¿Qué hace este módulo?
Define la interfaz de usuario (Streamlit), el proceso de despliegue en Oracle Cloud Free Tier y cómo mantener el sistema actualizado.

## Requisitos

### 1. Interfaz con Streamlit
- La interfaz permite subir documentos y hacer preguntas al agente.
- Cada respuesta muestra el texto generado y las citas de fuente.
- Se indica claramente que el usuario está hablando con un agente de IA.
- El historial de la conversación se preserva durante la sesión activa.

### 2. Elementos mínimos de la interfaz
- Campo de texto para preguntas
- Área de respuesta con texto + lista de fuentes
- Botones de feedback (👍 / 👎) por respuesta
- Sección de subida de documentos con confirmación de indexación

### 3. Despliegue en Oracle Cloud Free Tier
- La app corre en una VM ARM Ampere A1 (Ubuntu 22.04) — Always Free, sin expiración.
- Recursos disponibles: 2 OCPU, 12 GB RAM, 50 GB de block storage.
- FastAPI y Streamlit se exponen vía Nginx como reverse proxy.
- Los servicios se configuran con systemd para arranque automático.
- Chroma corre en la misma VM, guardando los vectores en disco (sin servidor externo).

### 4. Variables de entorno
- Todos los secrets (GEMINI_API_KEY, paths) están en el archivo `.env`.
- El `.env` nunca se sube al repositorio (está en `.gitignore`).
- Se provee un `.env.example` con todas las variables y sin valores reales.

### 5. Actualización de documentos
- Cuando se sube un documento nuevo o se reemplaza uno existente, el sistema lo reindexará automáticamente.
- No se requiere reiniciar el servidor para actualizar la base de conocimiento.

### 6. Logging básico
- Se registra cada pregunta: timestamp, pregunta, fallback_used, tiempo de respuesta y feedback del usuario.
- El log se guarda en un archivo JSONL local en la VM.

## Lo que está fuera del alcance
- HTTPS / SSL (opcional con Certbot, no requerido para el challenge)
- Panel de administración
- Autenticación de usuarios
- Detección automática de cambios en documentos externos
