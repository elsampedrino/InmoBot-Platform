from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.api_models import ChatMessageRequest, ChatMessageResponse
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> ChatMessageResponse:
    """
    Endpoint principal del pipeline conversacional.
    Recibe el mensaje del usuario y orquesta todo el flujo:
    tenant → contexto → router → parser/search/kb → IA → respuesta.
    """
    orchestrator = ChatOrchestrator(db)
    return await orchestrator.handle_message(request)
