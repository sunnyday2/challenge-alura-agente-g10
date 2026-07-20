import os
import uuid
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb

from app.config import settings
from app.exceptions import DocumentParseException, UnsupportedFormatException
from app.models.chunk import Chunk
from app.models.document import ParsedDocument
from app.parsers.parser_factory import get_parser
from app.parsers.text_cleaner import TextCleaner


class IngestionService:
    """
    Orquesta el pipeline completo de ingesta:
    parser → limpieza → chunking → embeddings → Chroma.
    """

    def __init__(self) -> None:
        self._cleaner = TextCleaner()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=f"models/{settings.gemini_embedding_model}",
            google_api_key=settings.gemini_api_key,
        )
        os.makedirs(settings.chroma_path, exist_ok=True)
        os.makedirs(settings.upload_path, exist_ok=True)

        self._chroma = chromadb.PersistentClient(path=settings.chroma_path)
        self._collection = self._chroma.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------

    def ingest(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Procesa un archivo y lo indexa en Chroma.

        Returns:
            ParsedDocument con los chunks generados.

        Raises:
            UnsupportedFormatException: formato no soportado.
            DocumentParseException: error extrayendo texto.
        """
        parser = get_parser(filename)
        extraction = parser.parse(content, filename)

        # Limpiar y unir bloques
        clean_blocks = [self._cleaner.clean(b.content) for b in extraction.blocks]
        clean_blocks = [b for b in clean_blocks if b]

        if not clean_blocks:
            raise DocumentParseException(filename, "No se pudo extraer texto del documento.")

        doc_type = os.path.splitext(filename)[1].lstrip(".").lower()

        # Borrar versión previa del documento si existe
        self._delete_existing(filename)

        # Generar chunks
        all_chunks: list[Chunk] = []
        global_idx = 0

        for block, orig_block in zip(clean_blocks, extraction.blocks):
            pieces = self._splitter.split_text(block)
            for piece in pieces:
                chunk = Chunk(
                    id=f"{filename}_{global_idx}",
                    content=piece,
                    source_filename=filename,
                    document_type=doc_type,
                    chunk_index=global_idx,
                    total_chunks=0,  # se actualiza abajo
                    page_number=orig_block.page_number,
                    section_title=orig_block.section_title,
                    slide_number=orig_block.slide_number,
                )
                all_chunks.append(chunk)
                global_idx += 1

        # Actualizar total_chunks
        total = len(all_chunks)
        for chunk in all_chunks:
            chunk.total_chunks = total

        # Generar embeddings e indexar en lotes
        self._index_chunks(all_chunks)

        # Guardar archivo en disco
        dest = os.path.join(settings.upload_path, filename)
        with open(dest, "wb") as f:
            f.write(content)

        return ParsedDocument(
            source_filename=filename,
            document_type=doc_type,
            raw_text_length=sum(len(b.content) for b in extraction.blocks),
            cleaned_text_length=sum(len(b) for b in clean_blocks),
            ocr_required=extraction.ocr_required,
            chunks=[],  # los chunks ya están en Chroma
            author=extraction.author,
            created_at=extraction.created_at,
        )

    # ------------------------------------------------------------------
    # Listar documentos indexados
    # ------------------------------------------------------------------

    def list_documents(self) -> list[dict]:
        """Devuelve una lista de documentos únicos con su chunk_count."""
        result = self._collection.get(include=["metadatas"])
        metadatas = result.get("metadatas") or []

        counts: dict[str, dict] = {}
        for meta in metadatas:
            fname = meta.get("source_filename", "unknown")
            if fname not in counts:
                counts[fname] = {
                    "filename": fname,
                    "document_type": meta.get("document_type", ""),
                    "chunk_count": 0,
                }
            counts[fname]["chunk_count"] += 1

        return list(counts.values())

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _delete_existing(self, filename: str) -> None:
        """Elimina chunks previos del mismo archivo del vector store."""
        try:
            existing = self._collection.get(
                where={"source_filename": filename},
                include=["metadatas"],
            )
            ids = existing.get("ids") or []
            if ids:
                self._collection.delete(ids=ids)
        except Exception:
            pass  # Si no existe, no hay nada que borrar

    def _index_chunks(self, chunks: list[Chunk], batch_size: int = 50) -> None:
        """Genera embeddings en lotes e indexa en Chroma."""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.content for c in batch]
            embeddings = self._embeddings.embed_documents(texts)
            self._collection.add(
                ids=[c.id for c in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[c.to_metadata() for c in batch],
            )
