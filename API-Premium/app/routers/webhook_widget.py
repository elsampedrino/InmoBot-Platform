from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.api_models import ChatMessageRequest, ChatMessageResponse, WebhookWidgetPayload
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()


@router.post("/widget", response_model=ChatMessageResponse)
async def webhook_widget(
    payload: WebhookWidgetPayload,
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """
    Recibe mensajes del widget web embebido.
    Normaliza el payload al formato interno y lo envía al orquestador.
    """
    request = ChatMessageRequest(
        empresa_slug=payload.empresa_slug,
        canal="web",
        session_id=payload.session_id,
        mensaje=payload.mensaje,
        metadata=payload.metadata,
    )
    orchestrator = ChatOrchestrator(db)
    return await orchestrator.handle_message(request)
