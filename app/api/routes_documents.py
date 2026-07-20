from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.exceptions import DocumentParseException, UnsupportedFormatException
from app.parsers.parser_factory import supported_extensions
from app.schemas.document import DocumentListResponse, DocumentListItem, DocumentUploadResponse
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def get_ingestion_service() -> IngestionService:
    """Dependency injection para IngestionService."""
    return IngestionService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir e indexar un documento",
)
async def upload_document(
    file: UploadFile,
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentUploadResponse:
    """
    Sube un documento y lo indexa en el vector store.

    Formatos soportados: pdf, docx, xlsx, pptx, md, csv, json, html, txt.
    Si el documento ya existía, sus chunks anteriores se reemplazan.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío.",
        )

    try:
        parsed = service.ingest(content, file.filename)
    except UnsupportedFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DocumentParseException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al procesar el documento: {e}",
        )

    # Contar chunks reales en Chroma para el documento
    docs = service.list_documents()
    chunk_count = next(
        (d["chunk_count"] for d in docs if d["filename"] == file.filename), 0
    )

    return DocumentUploadResponse(
        filename=file.filename,
        document_type=parsed.document_type,
        chunk_count=chunk_count,
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="Listar documentos indexados",
)
async def list_documents(
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentListResponse:
    """Devuelve todos los documentos actualmente indexados en el vector store."""
    docs = service.list_documents()
    items = [
        DocumentListItem(
            filename=d["filename"],
            document_type=d["document_type"],
            chunk_count=d["chunk_count"],
        )
        for d in docs
    ]
    return DocumentListResponse(documents=items)


@router.get(
    "/supported-formats",
    summary="Formatos de archivo soportados",
)
async def get_supported_formats() -> dict:
    """Lista las extensiones de archivo que el sistema puede procesar."""
    return {"extensions": supported_extensions()}
