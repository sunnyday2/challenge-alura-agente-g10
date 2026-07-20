from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Verifica que la API está en línea."""
    return HealthResponse(status="ok", message="RAG API is running.")
