from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Respuesta tras subir e indexar un documento."""

    filename: str
    document_type: str
    chunk_count: int
    message: str = "Documento indexado correctamente."


class DocumentListItem(BaseModel):
    """Ítem en el listado de documentos indexados."""

    filename: str
    document_type: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Listado completo de documentos en el vector store."""

    documents: list[DocumentListItem]
    total: int = Field(default=0)

    def model_post_init(self, __context) -> None:
        self.total = len(self.documents)
