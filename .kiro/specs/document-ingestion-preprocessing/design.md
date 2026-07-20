# Diseño — Ingesta y Preprocesamiento de Documentos

## Flujo general

```
POST /upload
    → IngestionService
        → ParserFactory  →  Parser específico  →  texto estructurado
        → TextCleaner    →  texto limpio
        → ChunkingService →  lista de chunks con metadatos
    ← respuesta JSON
```

## Componentes

### IngestionService
Orquesta todo el pipeline. Recibe el archivo (bytes + nombre + content-type) y devuelve el documento parseado con sus chunks.

### ParserFactory
Recibe el content-type o la extensión del archivo y devuelve el parser correspondiente.
Lanza `UnsupportedFormatException` si el formato no está soportado.

### Parsers (uno por formato)
| Parser | Librería | Qué extrae |
|---|---|---|
| PdfParser | PyMuPDF | Texto por página, detecta si necesita OCR |
| DocxParser | python-docx | Headings y párrafos en orden |
| XlsxParser | openpyxl | Filas de cada hoja como texto |
| PptxParser | python-pptx | Texto por slide + notas |
| MarkdownParser | BeautifulSoup | Texto plano conservando headings |
| CsvParser | stdlib | Filas como texto legible |
| JsonParser | stdlib | Objetos aplanados como texto |
| HtmlParser | BeautifulSoup | Texto sin tags HTML |
| TextParser | stdlib | Texto plano directo |

### TextCleaner
Función o clase simple que:
- Colapsa espacios duplicados
- Normaliza saltos de línea
- Elimina líneas en blanco repetidas y caracteres de control

### ChunkingService
Dos estrategias:
1. **Estructural**: usa los límites naturales del documento (páginas, secciones, slides)
2. **Por tamaño**: chunks de ~500–1000 caracteres con overlap cuando no hay estructura

## Modelos de datos

### ParsedDocument
```python
class ParsedDocument:
    source_filename: str
    document_type: str
    raw_text_length: int
    cleaned_text_length: int
    ocr_required: bool
    author: str | None
    created_at: str | None
    chunks: list[DocumentChunk]
```

### DocumentChunk
```python
class DocumentChunk:
    source_filename: str
    document_type: str
    chunk_index: int
    total_chunks: int
    content: str
    page_number: int | None
    section_title: str | None
    slide_number: int | None
    author: str | None
    created_at: str | None
```

## Respuesta de la API (upload exitoso)
```json
{
  "filename": "manual_empleados.pdf",
  "document_type": "pdf",
  "raw_text_length": 12034,
  "cleaned_text_length": 11480,
  "chunk_count": 22,
  "ocr_required": false,
  "metadata_sample": {
    "page_number": 1,
    "section_title": "Política de Vacaciones",
    "chunk_index": 0,
    "total_chunks": 22
  }
}
```
