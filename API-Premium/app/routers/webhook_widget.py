"""
webhook_widget.py — Endpoints públicos para el widget web embebido.

Rutas:
  GET  /webhook/{empresa_slug}/status  — estado del bot (bot_enabled, message)
  POST /webhook/{empresa_slug}/chat    — procesar mensaje conversacional

El empresa_slug viene en la URL porque el widget no lo incluye en el body;
solo envía { message, sessionId, timestamp, repo }.

La adaptación de contratos (widget ↔ interno) está completamente aislada
en app/adapters/widget_legacy.py.
"""
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.widget_legacy import (
    WidgetIncomingRequest,
    WidgetLegacyResponse,
    adapt_internal_response,
    adapt_widget_request,
)
from app.core.database import get_db
from app.models.db_models import Empresa
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()

_BOT_DISABLED_MSG = "El asistente virtual no está disponible en este momento."


# ── Status público ─────────────────────────────────────────────────────────────

class WidgetStatusResponse(BaseModel):
    bot_enabled: bool
    message: str | None = None


@router.get("/{empresa_slug}/status", response_model=WidgetStatusResponse)
async def widget_status(
    empresa_slug: str = Path(..., description="Slug de la empresa"),
    db: AsyncSession = Depends(get_db),
) -> WidgetStatusResponse:
    """
    Consulta pública que el widget llama al inicializar para saber si el bot
    está habilitado. No requiere autenticación.
    Si la empresa no existe, está inactiva o servicios.bot=false → bot_enabled=false.
    """
    result = await db.execute(
        select(Empresa.servicios, Empresa.activa).where(Empresa.slug == empresa_slug)
    )
    row = result.one_or_none()

    if not row or not row.activa:
        return WidgetStatusResponse(bot_enabled=False, message=_BOT_DISABLED_MSG)

    servicios: dict = row.servicios or {}
    bot_enabled = bool(servicios.get("bot", True))
    return WidgetStatusResponse(
        bot_enabled=bot_enabled,
        message=None if bot_enabled else _BOT_DISABLED_MSG,
    )


# ── Chat ───────────────────────────────────────────────────────────────────────

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
      2. ChatOrchestrator      → pipeline conversacional completo (incluye gate BOT_DISABLED)
      3. adapt_internal_response → traduce ChatMessageResponse → WidgetLegacyResponse
    """
    internal_request = adapt_widget_request(payload, empresa_slug)
    orchestrator = ChatOrchestrator(db)
    internal_response = await orchestrator.handle_message(internal_request)
    return adapt_internal_response(internal_response, payload.sessionId)
