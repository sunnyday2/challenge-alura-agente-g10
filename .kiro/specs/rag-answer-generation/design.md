# Diseño — Generación de Respuestas RAG

## Flujo general

```
Pregunta + contexto recuperado (chunks)
    → AnswerGenerationService
        → PromptBuilder        →  prompt con instrucciones de grounding
        → GeminiLLMProvider    →  respuesta cruda (gemini-2.5-flash)
        → AnswerValidator      →  ¿está soportada por el contexto?
            → si SÍ: CitationFormatter  →  respuesta + citas
            → si NO: FallbackPolicy     →  "no encontré esta información"
    ← respuesta estructurada
```

## Componentes

### AnswerGenerationService
Orquesta todo el flujo. Recibe la pregunta y los chunks del retrieval, devuelve la respuesta final.

### GeminiLLMProvider
Llama a `gemini-2.5-flash` via `google-genai`. Lee la API key desde `.env`.

```python
from google import genai

class GeminiLLMProvider:
    MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=prompt
        )
        return response.text

    def model_name(self) -> str:
        return self.MODEL
```

La misma `GEMINI_API_KEY` del `.env` sirve para LLM y embeddings.

### PromptBuilder
Arma el prompt con instrucción de grounding explícita:

```
Sos un asistente corporativo. Respondé SOLO usando los documentos que te doy.
Si la información no está en los documentos, decí exactamente:
"No encontré esta información en los documentos disponibles."
No inventes ni agregues información que no esté en el contexto.

DOCUMENTOS DE CONTEXTO:
[Documento: manual_empleados.pdf | Sección: Vacaciones | Página: 12]
Los empleados tienen 15 días hábiles de vacaciones por año...

PREGUNTA: ¿Cuántos días de vacaciones tengo?

Respondé en el mismo idioma de la pregunta.
```

### AnswerValidator
Verifica si la respuesta tiene soporte:
- Si no hay chunks recuperados → fallback inmediato
- Si los scores de similitud son todos muy bajos (< umbral configurable) → fallback
- Si la respuesta contiene la frase de "no encontré" → registrar como fallback

### CitationFormatter
Construye la lista de citas desde los metadatos de los chunks.
Solo incluye los campos que existen — no inventa nada.

### FallbackPolicy
Respuesta segura cuando no hay evidencia suficiente:
```json
{
  "answer": "No encontré esta información en los documentos disponibles.",
  "citations": [],
  "fallback_used": true,
  "fallback_reason": "no_context"
}
```

## Modelos de datos

### Citation
```python
class Citation:
    source_filename: str
    section_title: str | None
    page_number: int | None
    slide_number: int | None
    updated_at: str | None
```

### AnswerResponse
```python
class AnswerResponse:
    answer: str
    citations: list[Citation]
    fallback_used: bool
    fallback_reason: str | None  # "no_context", "low_confidence"
    model_name: str              # "gemini-2.5-flash"
```

## Respuestas de la API

### Respuesta exitosa
```json
{
  "answer": "Los empleados tienen 15 días hábiles de vacaciones por año.",
  "citations": [
    {
      "source_filename": "manual_empleados.pdf",
      "section_title": "Política de Vacaciones",
      "page_number": 12
    }
  ],
  "fallback_used": false,
  "fallback_reason": null,
  "model_name": "gemini-2.5-flash"
}
```

### Respuesta de fallback
```json
{
  "answer": "No encontré esta información en los documentos disponibles.",
  "citations": [],
  "fallback_used": true,
  "fallback_reason": "no_context",
  "model_name": "gemini-2.5-flash"
}
```

## Límites del plan gratuito de Gemini
- gemini-2.5-flash: 10 req/min, 500 req/día en free tier
- Para un demo estudiantil es más que suficiente
- Si se supera el límite, Gemini devuelve error 429 — el servicio debe manejarlo con un mensaje claro
