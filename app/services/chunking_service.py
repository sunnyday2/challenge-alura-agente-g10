from app.models.document import DocumentChunk
from app.parsers.base_parser import ExtractionResult


# Tamaño objetivo de chunk en caracteres (fallback por tamaño)
CHUNK_TARGET_SIZE = 800
CHUNK_OVERLAP = 150


class ChunkingService:
    """
    Divide el texto extraído en chunks con metadatos de origen.

    Estrategia 1 — Estructural: cuando el parser devuelve múltiples bloques
    (páginas, secciones, slides), cada bloque se convierte en un chunk.
    Bloques cortos consecutivos se fusionan para no generar chunks demasiado pequeños.

    Estrategia 2 — Por tamaño fijo: cuando hay un único bloque grande o los bloques
    son muy largos, se divide por caracteres con overlap.
    """

    def __init__(
        self,
        target_size: int = CHUNK_TARGET_SIZE,
        overlap: int = CHUNK_OVERLAP,
        min_block_size: int = 100,
    ):
        self.target_size = target_size
        self.overlap = overlap
        self.min_block_size = min_block_size

    def chunk(
        self,
        result: ExtractionResult,
        source_filename: str,
        document_type: str,
        author: str | None = None,
        created_at: str | None = None,
    ) -> list[DocumentChunk]:
        """Genera la lista final de DocumentChunks a partir de un ExtractionResult."""

        raw_chunks = self._split_into_raw_chunks(result)
        total = len(raw_chunks)

        return [
            DocumentChunk(
                source_filename=source_filename,
                document_type=document_type,
                chunk_index=i,
                total_chunks=total,
                content=chunk["content"],
                page_number=chunk.get("page_number"),
                section_title=chunk.get("section_title"),
                slide_number=chunk.get("slide_number"),
                author=author,
                created_at=created_at,
            )
            for i, chunk in enumerate(raw_chunks)
        ]

    def _split_into_raw_chunks(self, result: ExtractionResult) -> list[dict]:
        """Decide qué estrategia usar y devuelve lista de dicts con content + metadatos."""

        if not result.blocks:
            return []

        # Si hay múltiples bloques estructurados, usar estrategia estructural
        if len(result.blocks) > 1:
            return self._structural_chunks(result)

        # Bloque único: puede ser texto plano largo (CSV, JSON, TXT, etc.)
        single_block = result.blocks[0]
        if len(single_block.content) <= self.target_size:
            return [{
                "content": single_block.content,
                "page_number": single_block.page_number,
                "section_title": single_block.section_title,
                "slide_number": single_block.slide_number,
            }]

        # Texto largo: dividir por tamaño fijo con overlap
        return self._fixed_size_chunks(single_block)

    def _structural_chunks(self, result: ExtractionResult) -> list[dict]:
        """
        Convierte los bloques del parser en chunks.
        Fusiona bloques muy cortos con el siguiente. Divide bloques muy largos.
        """
        chunks: list[dict] = []
        pending: dict | None = None

        for block in result.blocks:
            text = block.content.strip()
            if not text:
                continue

            current = {
                "content": text,
                "page_number": block.page_number,
                "section_title": block.section_title,
                "slide_number": block.slide_number,
            }

            # Fusionar bloque muy corto con el anterior pendiente
            if pending and len(pending["content"]) < self.min_block_size:
                pending["content"] += "\n\n" + current["content"]
                continue

            if pending:
                # El bloque pendiente es suficientemente grande — subdividir si es necesario
                chunks.extend(self._maybe_split(pending))

            pending = current

        # Último bloque
        if pending:
            chunks.extend(self._maybe_split(pending))

        return chunks

    def _maybe_split(self, chunk: dict) -> list[dict]:
        """Si el bloque excede el tamaño máximo (2x target), lo divide con overlap."""
        if len(chunk["content"]) <= self.target_size * 2:
            return [chunk]

        sub_texts = self._split_text_with_overlap(chunk["content"])
        return [
            {**chunk, "content": text}
            for text in sub_texts
        ]

    def _fixed_size_chunks(self, block) -> list[dict]:
        """Divide un bloque largo en chunks de tamaño fijo con overlap."""
        texts = self._split_text_with_overlap(block.content)
        return [
            {
                "content": text,
                "page_number": block.page_number,
                "section_title": block.section_title,
                "slide_number": block.slide_number,
            }
            for text in texts
        ]

    def _split_text_with_overlap(self, text: str) -> list[str]:
        """
        Divide texto en segmentos de `target_size` con `overlap` de solapamiento.
        Intenta cortar en límites de párrafo o frase cuando es posible.
        """
        chunks: list[str] = []
        start = 0
        length = len(text)

        while start < length:
            end = min(start + self.target_size, length)

            # Intentar cortar en salto de línea o punto cercano al límite
            if end < length:
                # Buscar el último \n en el rango [end-100, end]
                cut = text.rfind("\n", max(start, end - 100), end)
                if cut == -1:
                    # Buscar el último espacio
                    cut = text.rfind(" ", max(start, end - 50), end)
                if cut != -1 and cut > start:
                    end = cut

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            # Avanzar con overlap
            start = end - self.overlap if end - self.overlap > start else end

        return chunks
