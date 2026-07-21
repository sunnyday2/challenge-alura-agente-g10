from fastapi import APIRouter, Depends, HTTPException, status

from app.exceptions import LLMException, RetrievalException
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, FeedbackRequest
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def get_rag_service() -> RAGService:
    """Dependency injection para RAGService."""
    return RAGService()


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    summary="Hacer una pregunta al agente RAG",
)
async def query(
    request: ChatQueryRequest,
    service: RAGService = Depends(get_rag_service),
) -> ChatQueryResponse:
    """
    Recibe una pregunta en lenguaje natural y devuelve la respuesta
    generada por Qwen3 basada en los documentos indexados,
    junto con las fuentes de donde proviene la información.

    Ejemplo de request:
    ```json
    { "question": "¿Cuál es la política de vacaciones?" }
    ```
    """
    try:
        return service.query(request.question)
    except RetrievalException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda semántica: {e}",
        )
    except LLMException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el modelo de lenguaje: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {e}",
        )


@router.post(
    "/feedback",
    status_code=status.HTTP_200_OK,
    summary="Registrar feedback sobre una respuesta",
)
async def feedback(
    request: FeedbackRequest,
    service: RAGService = Depends(get_rag_service),
) -> dict:
    """
    Guarda el feedback del usuario (👍 positive / 👎 negative)
    para una pregunta en el log JSONL.
    """
    try:
        service.record_feedback(request.question, request.feedback)
    except Exception:
        pass  # El feedback no debe fallar la respuesta
    return {"status": "ok", "feedback": request.feedback}
