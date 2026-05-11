"""
webhook_widget.py — Endpoints públicos para el widget web embebido.

Rutas:
  GET  /webhook/{empresa_slug}/status           — estado del bot
  POST /webhook/{empresa_slug}/chat             — procesar mensaje conversacional
  POST /webhook/{empresa_slug}/whatsapp-click   — registrar click en CTA WhatsApp
"""
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.widget_legacy import (
    WhatsAppHandoffPayload,
    WidgetIncomingRequest,
    WidgetLegacyResponse,
    adapt_internal_response,
    adapt_widget_request,
)
from app.core.database import get_db
from app.models.db_models import Empresa
from app.models.domain_models import ConversionEvent
from app.services.analytics_service import AnalyticsService
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.whatsapp_handoff import build_whatsapp_handoff

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
    internal_request = adapt_widget_request(payload, empresa_slug)
    orchestrator = ChatOrchestrator(db)
    internal_response = await orchestrator.handle_message(internal_request)
    response = adapt_internal_response(internal_response, payload.sessionId)

    # Inyectar WhatsApp handoff tras captura de lead (nombre confirmado)
    if internal_response.lead_capturado:
        empresa_result = await db.execute(
            select(Empresa.notificaciones, Empresa.id_empresa).where(Empresa.slug == empresa_slug)
        )
        row = empresa_result.one_or_none()
        if row:
            wa = (row.notificaciones or {}).get("whatsapp", {})
            if wa.get("enabled") and wa.get("phone"):
                nombre_lead = internal_response.metadata.get("nombre_lead")
                propiedades_interes = internal_response.metadata.get("propiedades_interes", [])
                payload_dict = build_whatsapp_handoff(
                    phone=wa["phone"],
                    agent_name=wa.get("agent_name", "Asesor"),
                    items=internal_response.items,
                    lead_nombre=nombre_lead,
                    propiedades_interes=propiedades_interes,
                )
                id_lead = internal_response.metadata.get("id_lead")
                response.whatsapp_handoff = WhatsAppHandoffPayload(
                    **payload_dict,
                    id_lead=id_lead,
                )

    return response


# ── Analytics: click WhatsApp ──────────────────────────────────────────────────

class WhatsAppClickRequest(BaseModel):
    session_id: str
    item_id: str | None = None
    id_lead: int | None = None


@router.post("/{empresa_slug}/whatsapp-click")
async def whatsapp_handoff_click(
    empresa_slug: str = Path(...),
    payload: WhatsAppClickRequest = ...,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Registra el evento analytics cuando el usuario hace click en el CTA de WhatsApp."""
    empresa_result = await db.execute(
        select(Empresa.id_empresa).where(Empresa.slug == empresa_slug)
    )
    row = empresa_result.one_or_none()
    if not row:
        return {"ok": False}

    analytics = AnalyticsService(db)
    await analytics.log_conversion_event(
        id_empresa=row.id_empresa,
        id_rubro=1,
        canal="web",
        evento=ConversionEvent.WHATSAPP_HANDOFF,
        id_lead=payload.id_lead,
        session_id=payload.session_id,
        metadata={"item_id": payload.item_id},
    )
    return {"ok": True}
