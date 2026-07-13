"""
Twilio WhatsApp webhook.

POST /webhook/twilio  → mensajes entrantes desde Twilio Sandbox (y producción futura)

Diferencias con Meta Cloud API:
  - Payload: form-encoded (no JSON)
  - Campos: From, To, Body, MessageSid
  - Respuesta: TwiML XML  o  silencio 200 (respondemos vía TwiML inline)
  - From tiene formato "whatsapp:+549..."  → strip del prefijo para normalizar
"""

import logging
import httpx
from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.api_models import ChatMessageRequest
from app.models.domain_models import ConversionEvent
from app.routers.webhook_whatsapp import (
    DOMAIN_SLUG,
    _log_whatsapp_analytics,
    _resolve_empresa,
    _should_notify_hours,
)
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.horario_service import is_bot_active
from app.repositories.empresas_repository import get_empresa_by_slug
from app.services.property_resolver import resolve_property
from app.services.tenant_resolver import TenantResolver

logger = logging.getLogger(__name__)
router = APIRouter()


def _twiml(body: str) -> Response:
    """Envuelve texto en TwiML para que Twilio lo envíe como mensaje."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f"<Message>{body}</Message>"
        "</Response>"
    )
    return Response(content=xml, media_type="application/xml")


def _normalize_number(wa_number: str) -> str:
    """'whatsapp:+5491159968052' → '5491159968052'"""
    return wa_number.replace("whatsapp:", "").replace("+", "").strip()


@router.post("/twilio")
async def receive_twilio(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Recibe mensajes de Twilio WhatsApp Sandbox."""
    from_number = _normalize_number(From)
    text = Body.strip()

    logger.info("Twilio WA message from %s: %.100s", from_number, text)

    empresa_slug = await _resolve_empresa(db, from_number, text)

    if not empresa_slug:
        return _twiml(
            "¡Hola! Para ayudarte mejor, por favor incluí el link a la propiedad que te interesa."
        )

    # ── Check modo de atención ────────────────────────────────────────────────
    empresa = await get_empresa_by_slug(db, empresa_slug)
    if empresa:
        active, reason = is_bot_active(empresa)
        if not active:
            if reason == "business_hours":
                if _should_notify_hours(from_number):
                    agent_phone = (empresa.notificaciones or {}).get("whatsapp", {}).get("phone", "").strip()
                    await _notify_agent_twilio(empresa, from_number, text)
                    await _log_whatsapp_analytics(
                        db, empresa_slug, empresa, from_number,
                        ConversionEvent.WHATSAPP_HANDOFF_BUSINESS_HOURS,
                        {"handoff_type": "business_hours", "agent_phone": agent_phone},
                    )
                    return _twiml(
                        f"¡Hola! 👋 Recibimos tu consulta. "
                        f"Un asesor de {empresa.nombre} se comunicará con vos a la brevedad."
                    )
            return Response(content="", status_code=200)

    # ── Bot activo en modo after_hours: registrar turno atendido por IA ────────
    if empresa and empresa.bot_mode == "after_hours":
        await _log_whatsapp_analytics(
            db, empresa_slug, empresa, from_number,
            ConversionEvent.WHATSAPP_BOT_AFTER_HOURS,
            {},
        )

    # ── Resolver propiedad por URL ────────────────────────────────────────────
    prop = None
    try:
        tenant = await TenantResolver(db).resolve(empresa_slug)
        if tenant:
            prop = await resolve_property(text, tenant.id_empresa, db)
    except Exception:
        logger.exception("Error en property_resolver para %s (Twilio)", from_number)

    if prop:
        calle  = prop.get("calle", "")
        barrio = prop.get("barrio", "")
        ubicacion = ", ".join(filter(None, [calle, barrio]))
        titulo = prop["titulo"]
        reply = (
            f"Hola! Vi que te interesa *{titulo}*"
            + (f" ({ubicacion})" if ubicacion else "")
            + ". Tengo informacion completa de esta propiedad. "
            + "Contame, que queres consultar? Puedo responder sobre disponibilidad, expensas, caracteristicas y mas."
        )
        try:
            from app.models.api_models import ChatMessageRequest as CMR
            silent_req = CMR(
                empresa_slug=empresa_slug,
                canal="whatsapp",
                session_id=from_number,
                mensaje="__property_link__",
                metadata={"message_id": MessageSid, "property_context": prop, "silent": True},
            )
            await ChatOrchestrator(db).handle_message(silent_req)
        except Exception:
            logger.exception("Error guardando property_context (Twilio) para %s", from_number)
        return _twiml(reply)

    # ── Orquestador ───────────────────────────────────────────────────────────
    req = ChatMessageRequest(
        empresa_slug=empresa_slug,
        canal="whatsapp",
        session_id=from_number,
        mensaje=text,
        metadata={"message_id": MessageSid},
    )
    try:
        resp = await ChatOrchestrator(db).handle_message(req)
        reply = resp.respuesta
    except Exception:
        logger.exception("Error en orquestador para Twilio de %s", from_number)
        reply = "Hubo un error procesando tu consulta. Intentá de nuevo en un momento."

    return _twiml(reply)


async def _notify_agent_twilio(empresa, from_number: str, text: str) -> None:
    """Notifica al agente vía Twilio REST API cuando el bot está en business_hours."""
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_FROM]):
        return
    agent_phone = (empresa.notificaciones or {}).get("whatsapp", {}).get("phone", "").strip()
    if not agent_phone:
        return
    body = f"📱 Nueva consulta por WhatsApp\nDe: +{from_number}\nMensaje: {text[:500]}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    wa_from = settings.TWILIO_WHATSAPP_FROM
    if not wa_from.startswith("whatsapp:"):
        wa_from = f"whatsapp:{wa_from}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            data={
                "From": wa_from,
                "To": f"whatsapp:+{agent_phone}",
                "Body": body,
            },
        )
    if resp.status_code not in (200, 201):
        logger.error("Twilio notify agent error %s: %s", resp.status_code, resp.text)