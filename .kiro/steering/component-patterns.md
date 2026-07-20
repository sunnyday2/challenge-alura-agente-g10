# component-patterns.md — Patrones del Proyecto

## Convenciones de nombres
| Artefacto | Convención | Ejemplo |
|---|---|---|
| Clases | PascalCase | IngestionService |
| Funciones y variables | snake_case | extract_text_from_pdf |
| Archivos y módulos | snake_case | routes_chat.py |
| Constantes | UPPER_SNAKE_CASE | MAX_CHUNK_SIZE |
| Tests | prefijo test_ | test_routes_chat.py |

## Patrones principales

### Capa de servicios
Los endpoints de FastAPI deben ser delgados (thin).
Toda la lógica va en los servicios: `IngestionService`, `RetrievalService`, `RAGService`.

### Parser Factory
Una fábrica que elige el parser correcto según el tipo de archivo subido.
Hace que agregar nuevos formatos sea fácil.

### Flujo RAG central (RAGService)
1. Recibe la pregunta del usuario
2. Recupera chunks relevantes del vector store
3. Construye el prompt
4. Llama a Bedrock
5. Devuelve la respuesta con las fuentes

## Estándares de código
- Usar type hints en funciones públicas
- Usar Pydantic para schemas de la API
- Route handlers cortos y legibles
- Docstrings en clases y métodos públicos

## Excepciones personalizadas
- `UnsupportedFormatException` — formato de archivo no soportado
- `DocumentParseException` — error al extraer texto
- `RetrievalException` — error en búsqueda semántica
- `LLMException` — error al llamar a Bedrock

## Qué evitar
- Lógica de negocio dentro de los route handlers
- Patrones enterprise complejos innecesarios para el challenge
- Capas de abstracción excesivas
