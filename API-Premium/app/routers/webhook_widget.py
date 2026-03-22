"""
webhook_widget.py — Endpoint público para el widget web embebido.

Ruta: POST /webhook/{empresa_slug}/chat

El empresa_slug viene en la URL porque el widget no lo incluye en el body;
solo envía { message, sessionId, timestamp, repo }.

La adaptación de contratos (widget ↔ interno) está completamente aislada
en app/adapters/widget_legacy.py.
"""
from fastapi import APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from app.core.database import get_db
from app.adapters.widget_legacy import (
    WidgetIncomingRequest,
    WidgetLegacyResponse,
    adapt_internal_response,
    adapt_widget_request,
)
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()


@router.post("/{empresa_slug}/chat", response_model=WidgetLegacyResponse)
async def webhook_widget_chat(
    empresa_slug: str = Path(..., description="Slug de la empresa (tenant)"),
    payload: WidgetIncomingRequest = ...,
    db: AsyncSession = Depends(get_db),
) -> WidgetLegacyResponse:
    """
    Recibe mensajes del widget web y devuelve la respuesta en el contrato
    legacy que el widget espera (compatible con el formato N8N existente).

    El widget apunta a: POST /webhook/{empresa_slug}/chat
    (configurado vía window.InmoBotConfig.apiUrl)

    Flujo:
      1. adapt_widget_request  → traduce { message, sessionId } → ChatMessageRequest
      2. ChatOrchestrator      → pipeline conversacional completo
      3. adapt_internal_response → traduce ChatMessageResponse → WidgetLegacyResponse
    """
    internal_request = adapt_widget_request(payload, empresa_slug)
    orchestrator = ChatOrchestrator(db)
    internal_response = await orchestrator.handle_message(internal_request)
    return adapt_internal_response(internal_response, payload.sessionId)
