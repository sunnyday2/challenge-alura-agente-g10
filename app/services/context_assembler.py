from app.models.retrieval import RetrievedChunk


class ContextAssembler:
    """Ensambla los chunks recuperados en un bloque de texto para el prompt del LLM."""

    def assemble(self, chunks: list[RetrievedChunk]) -> str:
        """
        Construye el bloque de contexto con labels de fuente por chunk.

        Formato:
            [Documento: archivo.pdf | Sección: Titulo | Página: 3]
            Contenido del chunk...
        """
        parts: list[str] = []
        for chunk in chunks:
            label = self._build_label(chunk)
            parts.append(f"{label}\n{chunk.content.strip()}")
        return "\n\n".join(parts)

    def _build_label(self, chunk: RetrievedChunk) -> str:
        fields = [f"Documento: {chunk.source_filename}"]
        if chunk.section_title:
            fields.append(f"Sección: {chunk.section_title}")
        if chunk.page_number and chunk.page_number > 0:
            fields.append(f"Página: {chunk.page_number}")
        if chunk.slide_number and chunk.slide_number > 0:
            fields.append(f"Slide: {chunk.slide_number}")
        return "[" + " | ".join(fields) + "]"
