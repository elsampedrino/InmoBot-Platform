"""
WhatsApp Business Cloud API webhook.

GET  /webhook/whatsapp  → verificación del webhook por Meta
POST /webhook/whatsapp  → mensajes entrantes → orquestador → respuesta vía Graph API

Flujo de resolución de empresa:
  1. Mensaje contiene URL de propiedad → extraer dominio → DOMAIN_SLUG
  2. Usuario recurrente → buscar conversación abierta por número de teléfono
"""

import re
import logging
import httpx
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.api_models import ChatMessageRequest
from app.models.db_models import Conversacion, Empresa
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.property_resolver import resolve_property
from app.services.tenant_resolver import TenantResolver

logger = logging.getLogger(__name__)
router = APIRouter()

# Dominio del sitio web del cliente → empresa_slug en nuestra DB
# Agregar nuevos clientes acá cuando se sumen al canal WhatsApp
DOMAIN_SLUG: dict[str, str] = {
    "pablohoughton.com.ar":            "houghton",
    "brucellariabienesraices.com.ar":  "cristian-inmob",
}


# ── Verificación ──────────────────────────────────────────────────────────────

@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> Response:
    """Meta llama a este endpoint para verificar la URL del webhook."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verificado correctamente")
        return Response(content=hub_challenge or "", media_type="text/plain")
    logger.warning("Intento de verificación WhatsApp con token inválido")
    return Response(status_code=403)


# ── Mensajes entrantes ────────────────────────────────────────────────────────

@router.post("/whatsapp")
async def receive_whatsapp(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Recibe el payload raw de Meta y procesa los mensajes de texto entrantes."""
    body = await request.json()

    if body.get("object") != "whatsapp_business_account":
        return Response(content="ok")

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                continue
            phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
            for msg in messages:
                if msg.get("type") != "text":
                    continue
                await _handle_message(
                    db=db,
                    from_number=msg["from"],
                    message_id=msg["id"],
                    text=msg["text"]["body"],
                    phone_number_id=phone_number_id,
                )

    # Meta requiere 200 rápido; el procesamiento ya es async
    return Response(content="ok")


# ── Lógica interna ────────────────────────────────────────────────────────────

async def _handle_message(
    db: AsyncSession,
    from_number: str,
    message_id: str,
    text: str,
    phone_number_id: str,
) -> None:
    empresa_slug = await _resolve_empresa(db, from_number, text)

    if not empresa_slug:
        logger.warning("No se pudo resolver empresa para %s: %.100s", from_number, text)
        await _send_reply(
            phone_number_id, from_number,
            "¡Hola! Para ayudarte mejor, por favor incluí el link a la propiedad que te interesa.",
        )
        return

    # Intentar identificar propiedad específica por Tokko ID en la URL
    prop = None
    try:
        tenant = await TenantResolver(db).resolve(empresa_slug)
        if tenant:
            prop = await resolve_property(text, tenant.id_empresa, db)
    except Exception:
        logger.exception("Error en property_resolver para %s", from_number)

    # Mensaje 1 del flujo Yamila: el usuario manda solo el link de la propiedad.
    # Respondemos con un saludo fijo y guardamos la propiedad en el orchestrator
    # vía metadata para el siguiente turno. NO llamamos al AI aquí.
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
        # Guardamos la propiedad en el estado conversacional para el siguiente turno
        # pasando property_context al orchestrator con un mensaje interno silencioso
        try:
            silent_req = ChatMessageRequest(
                empresa_slug=empresa_slug,
                canal="whatsapp",
                session_id=from_number,
                mensaje="__property_link__",
                metadata={"message_id": message_id, "property_context": prop, "silent": True},
            )
            await ChatOrchestrator(db).handle_message(silent_req)
        except Exception:
            logger.exception("Error guardando property_context en estado para %s", from_number)
        await _send_reply(phone_number_id, from_number, reply)
        return

    metadata: dict = {"message_id": message_id}
    req = ChatMessageRequest(
        empresa_slug=empresa_slug,
        canal="whatsapp",
        session_id=from_number,
        mensaje=text,
        metadata=metadata,
    )

    try:
        resp = await ChatOrchestrator(db).handle_message(req)
        reply = resp.respuesta
    except Exception:
        logger.exception("Error en orquestador para mensaje WhatsApp de %s", from_number)
        reply = "Hubo un error procesando tu consulta. Intentá de nuevo en un momento."

    await _send_reply(phone_number_id, from_number, reply)


async def _resolve_empresa(db: AsyncSession, from_number: str, text: str) -> str | None:
    """
    Estrategia 1: el mensaje contiene una URL → extraer dominio → DOMAIN_SLUG.
    Estrategia 2: usuario recurrente → buscar conversación WhatsApp abierta.
    """
    match = re.search(r"https?://(?:www\.)?([^/\s]+)", text)
    if match:
        slug = DOMAIN_SLUG.get(match.group(1))
        if slug:
            return slug

    result = await db.execute(
        select(Empresa.slug)
        .join(Conversacion, Empresa.id_empresa == Conversacion.id_empresa)
        .where(
            Conversacion.session_id == from_number,
            Conversacion.canal == "whatsapp",
            Conversacion.fin.is_(None),
        )
        .order_by(Conversacion.created_at.desc())
        .limit(1)
    )
    row = result.first()
    return row[0] if row else None


async def _send_reply(phone_number_id: str, to: str, text: str) -> None:
    """Envía respuesta de texto via Meta Graph API."""
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
        )
    if resp.status_code != 200:
        logger.error("Meta Graph API error %s: %s", resp.status_code, resp.text)
