from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.api_models import ChatMessageRequest, ChatMessageResponse, WebhookWhatsAppPayload
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()


@router.post("/whatsapp", response_model=ChatMessageResponse)
async def webhook_whatsapp(
    payload: WebhookWhatsAppPayload,
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """
    Recibe webhooks de WhatsApp Business.
    Normaliza el payload al formato interno y lo envía al orquestador.
    """
    request = ChatMessageRequest(
        empresa_slug=payload.empresa_slug,
        canal="whatsapp",
        session_id=payload.phone_number,
        mensaje=payload.mensaje,
        metadata={**payload.metadata, "message_id": payload.message_id},
    )
    orchestrator = ChatOrchestrator(db)
    return await orchestrator.handle_message(request)
