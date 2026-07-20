# Requisitos — Ingesta y Preprocesamiento de Documentos

## ¿Qué hace este módulo?
Recibe archivos subidos por el usuario, extrae el texto, lo limpia y lo divide en chunks con metadatos.
La salida de este módulo son los chunks que luego se van a indexar en el vector store.

## Requisitos

### 1. Soporte de múltiples formatos
- El sistema detecta el tipo de archivo y elige el parser correcto.
- Formatos soportados: PDF, DOCX, XLSX, PPTX, Markdown, CSV, JSON, HTML, TXT.
- Si el formato no es soportado, se devuelve un error claro al usuario.
- Los PDFs sin texto extraíble se marcan como `ocr_required = True` (sin procesar OCR por ahora).

### 2. Limpieza del texto extraído
- Normalizar espacios y saltos de línea.
- Eliminar líneas vacías repetidas y caracteres de control.
- Conservar la estructura útil: títulos, párrafos, separación de slides, etc.

### 3. División en chunks
- Preferir chunks basados en estructura del documento (sección, párrafo, slide).
- Si no hay estructura, usar chunking por tamaño fijo (~500–1000 caracteres) con overlap.
- Mantener el título pegado al primer párrafo cuando sea posible.

### 4. Metadatos por chunk
Cada chunk debe tener:
- Nombre del archivo fuente
- Tipo de documento
- Índice del chunk y total de chunks
- Número de página, título de sección o número de slide (cuando esté disponible)
- Autor y fechas del archivo (cuando estén disponibles)

### 5. Integración con la API
- El endpoint `POST /api/v1/documents/upload` ejecuta todo el pipeline.
- Si todo sale bien, devuelve: nombre del archivo, tipo, longitud del texto, cantidad de chunks y una muestra de metadatos.
- Si algo falla, devuelve un error legible.
