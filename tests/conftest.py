"""
Configuración global de pytest.

Tests que requieren langchain, chromadb o modelos IA están en:
  - test_chunking.py       → requiere langchain
  - test_ingestion_service.py → requiere langchain + parsers
  - test_retrieval.py      → requiere langchain-google-genai + chromadb (mockeado)
  - test_rag_service.py    → requiere langchain-ollama (mockeado)

Para correr solo los tests sin dependencias externas:
  pytest tests/test_exceptions.py tests/test_schemas.py tests/test_parser_factory.py
         tests/test_parsers.py tests/test_text_cleaner.py tests/test_indexing.py

Para correr todos (con el venv del proyecto activado):
  pytest
"""
