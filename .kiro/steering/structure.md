# structure.md — Estructura del Proyecto

```
challenge-alura-agente-g10/
├── app/
│   ├── main.py               # Punto de entrada de FastAPI
│   ├── config.py             # Variables de entorno y configuración
│   ├── api/
│   │   ├── routes_documents.py   # Subida de documentos
│   │   ├── routes_chat.py        # Preguntas al agente
│   │   └── routes_health.py      # Health check
│   ├── schemas/
│   │   ├── document.py       # Schemas Pydantic de documentos
│   │   └── chat.py           # Schemas Pydantic de chat
│   ├── services/
│   │   ├── ingestion_service.py  # Procesa archivos subidos
│   │   ├── retrieval_service.py  # Búsqueda semántica
│   │   └── rag_service.py        # Orquesta el flujo RAG completo
│   ├── parsers/
│   │   ├── base_parser.py    # Contrato común para parsers
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── xlsx_parser.py
│   │   ├── pptx_parser.py
│   │   ├── markdown_parser.py
│   │   ├── csv_parser.py
│   │   ├── json_parser.py
│   │   ├── html_parser.py
│   │   └── parser_factory.py # Elige el parser según el tipo de archivo
│   └── models/
│       ├── document.py       # Modelo interno de documento
│       └── chunk.py          # Modelo interno de chunk
├── data/                     # Archivos subidos y vector store local
├── tests/                    # Pruebas unitarias
├── streamlit_app.py          # Interfaz web para la demo
├── requirements.txt
└── README.md
```

## Responsabilidades
- `api/` — rutas HTTP (thin, sin lógica de negocio)
- `services/` — toda la lógica: ingesta, retrieval, RAG
- `parsers/` — extracción de texto por formato de archivo
- `schemas/` — modelos Pydantic para request/response de la API
- `models/` — entidades internas de la aplicación

## Regla principal
Los route handlers no deben tener lógica. Todo va en los servicios.
