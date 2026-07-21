# tech.md — Stack Técnico

## Stack principal
| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| Validación | Pydantic v2 |
| LLM | Google Gemini (gemini-2.5-flash) — API gratuita |
| Embeddings | Google Gemini (text-embedding-004) — API gratuita |
| RAG | LangChain |
| Vector Store | Chroma (local, en disco) |
| Interfaz | Streamlit |
| Despliegue | Oracle Cloud Free Tier — VM ARM A1 (Ubuntu 22.04) |

## Por qué Gemini
- API key gratuita en https://aistudio.google.com/apikey
- Plan gratuito: 15 req/min, 1.500 req/día para Flash, sin tarjeta de crédito
- Un mismo proveedor para LLM + embeddings — una sola API key en el `.env`
- Librería oficial: `google-genai`
- Sin dependencia de AWS ni credenciales de nube

## Por qué Oracle Cloud Free Tier
- VM ARM (Ampere A1): 2 OCPU + 12 GB RAM — Always Free, sin expiración
  - ⚠️ Desde junio 2026 el límite bajó de 4 OCPU/24 GB a 2 OCPU/12 GB
- 50 GB de block storage Always Free (suficiente para Chroma + app)
- IP pública incluida
- Chroma corre local en la VM — sin necesidad de base de datos externa

## Flujo RAG
1. El usuario sube un documento a FastAPI
2. El backend detecta el tipo de archivo
3. El parser extrae el texto
4. El texto se divide en chunks
5. Se generan embeddings con Gemini text-embedding-004 y se guardan en Chroma
6. El usuario hace una pregunta
7. La pregunta se convierte en embedding con el mismo modelo
8. Chroma busca los chunks más similares
9. Gemini Flash genera la respuesta usando solo los chunks encontrados
10. FastAPI devuelve la respuesta + las fuentes

## Librerías por formato de archivo
| Formato | Librería |
|---|---|
| PDF | PyMuPDF |
| DOCX | python-docx |
| XLSX | openpyxl |
| PPTX | python-pptx |
| Markdown / HTML | BeautifulSoup |
| CSV / JSON / TXT | Librería estándar de Python |

## Librerías de IA
| Propósito | Librería |
|---|---|
| LLM + Embeddings | `google-genai` |
| RAG orchestration | `langchain`, `langchain-google-genai` |
| Vector store | `chromadb` |

## Principios para el código
- Endpoints delgados, lógica en servicios
- Modelos Pydantic para request y response
- JSON consistente en todas las respuestas
- Setup local simple, sin infra complicada
- Swagger activado para mostrar en la presentación
- Secrets solo en `.env`, nunca hardcodeados
