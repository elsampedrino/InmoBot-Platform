"""
widget_legacy.py — Adapter entre el contrato interno Premium y el contrato
legacy que consume el widget embebido (Básico / PRO / Premium).

─── Contratos ────────────────────────────────────────────────────────────────

  WIDGET → API (request)
    { message, sessionId, timestamp, repo }

  API (interno) ← ChatMessageResponse
    { session_id, conversation_id, respuesta, items[], route, stage,
      lead_capturado, metadata }

  API → WIDGET (response legacy)
    { success, response, sessionId, propiedades_detalladas[], leads,
      propiedadesMostradas, timestamp }

─── Responsabilidades ────────────────────────────────────────────────────────
  - Traducir el request del widget al formato interno de la API Premium.
  - Traducir la respuesta interna al contrato legacy que el widget lee.
  - NO contiene lógica de negocio; solo mapeo de campos.
  - NO depende del ORM, base de datos ni servicios externos.

─── Mapeo de propiedades ─────────────────────────────────────────────────────
  ItemBrief.id_item              → propiedades[].id
  ItemBrief.titulo               → propiedades[].titulo  (campo extra tolerado)
  ItemBrief.atributos.tipo       → propiedades[].tipo
  ItemBrief.atributos.operacion  → propiedades[].operacion
  ItemBrief.precio + moneda      → propiedades[].precio.{valor, moneda}
  ItemBrief.atributos.{barrio,ciudad,provincia} → propiedades[].direccion
  ItemBrief.atributos.{dormitorios,ambientes,superficie_total} → .caracteristicas
  ItemBrief.atributos.detalles   → propiedades[].detalles
  ItemBrief.fotos                → propiedades[].imagenes
  ItemBrief.descripcion_corta    → propiedades[].descripcion
"""
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.models.api_models import ChatMessageRequest, ChatMessageResponse, ItemBrief


# ─── Request del widget ───────────────────────────────────────────────────────

class WidgetIncomingRequest(BaseModel):
    """
    Payload que envía el widget web al hacer POST al endpoint.

    Campos que manda el widget actual:
      message   — texto del usuario
      sessionId — ID de sesión generado por el widget
      timestamp — ISO string del momento del envío
      repo      — identificador de instancia del widget ('bbr', 'demo', etc.)
    """
    message: str = Field(..., min_length=1, max_length=2000)
    sessionId: str
    timestamp: str = Field(default="")
    repo: str = Field(default="")


# ─── Response legacy ──────────────────────────────────────────────────────────

class _LegacyPrecio(BaseModel):
    valor: float | None = None
    moneda: str = "USD"


class _LegacyDireccion(BaseModel):
    barrio: str = ""
    ciudad: str = ""
    provincia: str = ""


class _LegacyCaracteristicas(BaseModel):
    dormitorios: int | None = None
    ambientes: int | None = None
    superficie_total: float | None = None


class LegacyPropertyResponse(BaseModel):
    """Propiedad en el formato que renderiza el widget."""
    id: str
    titulo: str = ""
    tipo: str = ""
    operacion: str = ""
    precio: _LegacyPrecio | None = None
    direccion: _LegacyDireccion = Field(default_factory=_LegacyDireccion)
    caracteristicas: _LegacyCaracteristicas = Field(default_factory=_LegacyCaracteristicas)
    detalles: list[str] = []
    imagenes: list[str] = []
    descripcion: str = ""


class WidgetLegacyResponse(BaseModel):
    """
    Contrato de salida que el widget embebido espera recibir.

    El widget lee (con fallbacks):
      data.response || data.respuesta_bot       → texto del bot
      data.propiedades_detalladas || data.propiedades → listado de propiedades
      data.leads === true                        → muestra botones de acción
      data.metricas || data.costos              → métricas opcionales (ignorado si null)
    """
    success: bool = True
    response: str
    sessionId: str
    propiedades_detalladas: list[LegacyPropertyResponse] = []
    propiedadesMostradas: int = 0
    leads: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # Campo opcional de métricas — el widget lo ignora si es null
    metricas: dict[str, Any] | None = None


# ─── Funciones de adaptación ──────────────────────────────────────────────────

def adapt_widget_request(
    payload: WidgetIncomingRequest,
    empresa_slug: str,
) -> ChatMessageRequest:
    """
    Convierte el payload del widget al formato interno de la API Premium.

    empresa_slug viene de la URL (/{empresa_slug}/widget/chat), no del body,
    ya que el widget no envía ese campo.
    """
    return ChatMessageRequest(
        empresa_slug=empresa_slug,
        canal="web",
        session_id=payload.sessionId,
        mensaje=payload.message,
        metadata={"repo": payload.repo, "widget_timestamp": payload.timestamp},
    )


def adapt_internal_response(
    internal: ChatMessageResponse,
    session_id: str,
) -> WidgetLegacyResponse:
    """
    Convierte la respuesta interna Premium al contrato legacy del widget.

    Reglas de mapeo:
    - response       ← internal.respuesta
    - propiedades_detalladas ← internal.items (mapeados con _item_to_legacy)
    - leads          ← True cuando hay propiedades mostradas (activa botones en widget)
    - metricas       ← subset no sensible de metadata (response_time, route)
    """
    propiedades = [_item_to_legacy(it) for it in internal.items]

    metricas = {
        "response_time_ms": internal.metadata.get("response_time_ms"),
        "route": internal.route,
        "total_encontrados": internal.metadata.get("total_encontrados"),
    } if internal.metadata else None

    return WidgetLegacyResponse(
        success=True,
        response=internal.respuesta,
        sessionId=session_id,
        propiedades_detalladas=propiedades,
        propiedadesMostradas=len(propiedades),
        leads=False,  # Plan Premium: captura de leads solo vía flujo conversacional
        metricas=metricas,
    )


def _item_to_legacy(item: ItemBrief) -> LegacyPropertyResponse:
    """Mapea un ItemBrief interno al formato de propiedad que renderiza el widget."""
    atrib: dict[str, Any] = item.atributos or {}

    precio = None
    if item.precio is not None:
        precio = _LegacyPrecio(
            valor=item.precio,
            moneda=item.moneda or "USD",
        )

    direccion = _LegacyDireccion(
        barrio=str(atrib.get("barrio") or atrib.get("zona") or ""),
        ciudad=str(atrib.get("ciudad") or ""),
        provincia=str(atrib.get("provincia") or ""),
    )

    caracteristicas = _LegacyCaracteristicas(
        dormitorios=_int_or_none(atrib.get("dormitorios")),
        ambientes=_int_or_none(atrib.get("ambientes")),
        superficie_total=_float_or_none(
            atrib.get("superficie_total") or atrib.get("superficie")
        ),
    )

    detalles = atrib.get("detalles") or []
    if isinstance(detalles, str):
        detalles = [detalles]

    return LegacyPropertyResponse(
        id=item.id_item,
        titulo=item.titulo,
        tipo=item.tipo or str(atrib.get("tipo") or ""),
        operacion=item.categoria or str(atrib.get("operacion") or ""),
        precio=precio,
        direccion=direccion,
        caracteristicas=caracteristicas,
        detalles=[str(d) for d in detalles],
        imagenes=item.fotos or [],
        descripcion=item.descripcion_corta or "",
    )


def _int_or_none(val: Any) -> int | None:
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _float_or_none(val: Any) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None
