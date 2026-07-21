# product.md — Descripción del Proyecto

## ¿Qué es esto?
Un asistente de IA que responde preguntas sobre documentos internos de una empresa ficticia.
Usa RAG (Retrieval-Augmented Generation) con un agente que busca en los documentos antes de responder.

## Objetivo del Challenge
Construir una API con FastAPI que:
1. Reciba documentos (PDF, Word, Excel, etc.) y los procese
2. Permita hacer preguntas en lenguaje natural
3. Responda con información del documento + la fuente de donde vino

## Usuarios
- Empleados que buscan información de la empresa
- El evaluador del challenge que va a probar la API

## Funciones principales
1. Subir y procesar documentos
2. Soportar PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON, HTML
3. Responder preguntas via API
4. Incluir fuente/referencia en cada respuesta
5. Tener una interfaz simple (Streamlit) para la demo

## Stack de IA
- **LLM y embeddings**: Google Gemini (API gratuita, sin tarjeta de crédito)
- **Vector store**: Chroma (corre localmente en la VM)
- **Despliegue**: Oracle Cloud Free Tier — VM ARM Ampere A1 (Always Free, sin expiración)

## Criterios de éxito
- La API responde preguntas basadas en los documentos subidos
- Cada respuesta incluye de dónde viene la información
- El proyecto corre en Oracle Cloud Free Tier sin costo
- El código es legible y fácil de explicar en la presentación

## Fuera del alcance
- Login / control de acceso
- Panel de administración
- Procesar audio o video
- Base de datos externa (Chroma es suficiente)
