# Tareas — Ingesta y Preprocesamiento de Documentos

- [ ] 1. Crear los modelos `ParsedDocument` y `DocumentChunk` en `app/models/`

- [ ] 2. Crear `ParserFactory` en `app/parsers/parser_factory.py`
  - Mapear extensiones/MIME types a parsers
  - Lanzar `UnsupportedFormatException` si el formato no está soportado

- [ ] 3. Implementar los parsers en `app/parsers/`
  - [ ] 3.1 `PdfParser` — texto por página, detectar OCR requerido
  - [ ] 3.2 `DocxParser` — headings y párrafos
  - [ ] 3.3 `XlsxParser` — filas de hojas como texto
  - [ ] 3.4 `PptxParser` — texto por slide + notas
  - [ ] 3.5 `MarkdownParser`, `CsvParser`, `JsonParser`, `HtmlParser`, `TextParser`

- [ ] 4. Implementar `TextCleaner` — normalizar espacios, saltos de línea, eliminar ruido

- [ ] 5. Implementar `ChunkingService`
  - [ ] 5.1 Chunking estructural (por páginas/secciones/slides)
  - [ ] 5.2 Chunking por tamaño fijo con overlap como fallback

- [ ] 6. Implementar `IngestionService` que orqueste todo el pipeline

- [ ] 7. Conectar con el endpoint `POST /api/v1/documents/upload`
  - Devolver el resumen JSON con filename, tipo, longitudes, chunk count, OCR flag y muestra de metadatos

- [ ] 8. Escribir tests básicos
  - [ ] 8.1 Test de selección de parser por extensión
  - [ ] 8.2 Test de extracción para Markdown, CSV y JSON
  - [ ] 8.3 Test de chunking y overlap
  - [ ] 8.4 Test del pipeline completo de ingesta
