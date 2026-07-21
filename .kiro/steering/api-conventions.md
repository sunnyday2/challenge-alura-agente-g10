# api-conventions.md — Convenciones de la API

## Base Path
`/api/v1`

## Endpoints principales
- `POST /api/v1/documents/upload` — subir un documento
- `GET  /api/v1/documents` — listar documentos subidos
- `POST /api/v1/chat/query` — hacer una pregunta al agente RAG
- `GET  /api/v1/health` — health check

## Reglas de request/response
- JSON para requests y responses estándar
- `multipart/form-data` para subida de archivos
- Schemas definidos con Pydantic
- Errores con mensajes legibles

## Ejemplo de pregunta al agente
```json
// POST /api/v1/chat/query
{ "question": "¿Cuál es la política de vacaciones?" }
```

```json
// Respuesta
{
  "answer": "Los empleados pueden solicitar vacaciones desde el portal de RRHH.",
  "sources": [
    { "document": "manual_empleados.pdf", "section": "Vacaciones", "page": 12 }
  ]
}
```

## Códigos de estado
- `200` — OK
- `201` — Documento subido
- `400` — Input inválido
- `404` — No encontrado
- `422` — Error de validación
- `500` — Error interno

## Convenciones FastAPI
- Organizar endpoints con `APIRouter`
- Mantener Swagger activado (`/docs`)
- Preferir endpoints async
- HTTP en routes, lógica en services
