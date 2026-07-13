"""
cliente_dashboard.py — Dashboard omnicanal para el usuario cliente (inmobiliaria).

Ruta: GET /cliente/dashboard?periodo=mes_actual|7d|30d|90d

Arquitectura: el rendimiento por canal se calcula vía CHANNEL_PROVIDERS
(ver app/services/channel_metrics.py). Cada canal decide si está habilitado
para la empresa y calcula sus propias métricas — este endpoint no contiene
lógica específica de WhatsApp ni de Web, solo itera la lista de providers.
Sumar un canal nuevo (Instagram DM, Messenger, Telegram...) no requiere
modificar este archivo.

Devuelve en una sola llamada:
  - summary: KPIs globales de la empresa, independientes de canal
  - channels: rendimiento por canal habilitado (lista dinámica)
  - leads_recientes: últimos 15 leads, con canal de origen
  - actividad: conversaciones globales del período + promedio diario
  - rankings: propiedades con más leads / más consultadas sin lead
  - alertas: alertas operativas simples

TODO (futura sección "Atención fuera de horario"):
  - consultas_fuera_horario (whatsapp_bot_after_hours)
  - leads_generados_fuera_horario (leads where canal=whatsapp + conversion after_hours)
  - tasa_conversion_after_hours
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin
from app.services.channel_metrics import CHANNEL_PROVIDERS, ChannelBlock

router = APIRouter()

# Rubro inmobiliaria — único punto de definición para este módulo
_ID_RUBRO_INMOBILIARIA = 1

_PERIODOS_VALIDOS = {"mes_actual", "7d", "30d", "90d"}


def _calcular_desde(periodo: str) -> datetime:
    """Devuelve el datetime UTC de inicio del período solicitado."""
    now = datetime.now(timezone.utc)
    if periodo == "7d":
        return now - timedelta(days=7)
    if periodo == "30d":
        return now - timedelta(days=30)
    if periodo == "90d":
        return now - timedelta(days=90)
    # mes_actual (default)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# ─── Modelos de respuesta ─────────────────────────────────────────────────────

class Summary(BaseModel):
    leads_periodo: int
    leads_nuevos: int
    consultas_periodo: int
    propiedades_activas: int
    canales_activos: int
    canales_disponibles: int   # preparado para upsell futuro, no destacado en UI todavía


class LeadResumen(BaseModel):
    fecha: str
    nombre: str | None
    telefono: str | None
    propiedad_titulo: str | None
    estado: str
    canal: str


class Actividad(BaseModel):
    conversaciones_periodo: int
    promedio_diario: float


class PropConLeads(BaseModel):
    external_id: str        # identificador principal (ej: PROP-001)
    titulo: str
    ubicacion: str | None
    leads_periodo: int


class PropConsultada(BaseModel):
    external_id: str
    titulo: str
    ubicacion: str | None
    consultas_periodo: int


class Rankings(BaseModel):
    props_con_leads: list[PropConLeads]
    props_consultadas: list[PropConsultada]


class AlertaCliente(BaseModel):
    tipo: str
    mensaje: str


class ClienteDashboardResponse(BaseModel):
    empresa_nombre: str
    periodo: str
    generado_en: str
    summary: Summary
    channels: list[ChannelBlock]
    leads_recientes: list[LeadResumen]
    actividad: Actividad
    rankings: Rankings
    alertas: list[AlertaCliente]


# ─── Helper ───────────────────────────────────────────────────────────────────

def _ubicacion(atributos: dict | None) -> str | None:
    if not atributos:
        return None
    barrio  = atributos.get("barrio")
    ciudad  = atributos.get("ciudad")
    partes  = [p for p in [barrio, ciudad] if p]
    return ", ".join(partes) if partes else None


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.get("", response_model=ClienteDashboardResponse)
async def get_cliente_dashboard(
    periodo: str = Query("mes_actual", description="Período: mes_actual | 7d | 30d | 90d"),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    if periodo not in _PERIODOS_VALIDOS:
        periodo = "mes_actual"
    emp   = current_user.id_empresa
    desde = _calcular_desde(periodo)

    # ── Empresa: nombre, servicios (para habilitar canales), notificaciones, catálogo ──
    config_row = await db.execute(text("""
        SELECT e.nombre, e.servicios, e.notificaciones, erc.github_repo
        FROM empresas e
        LEFT JOIN empresa_rubro_catalogos erc
               ON erc.id_empresa = e.id_empresa AND erc.id_rubro = :rubro
        WHERE e.id_empresa = :emp
    """), {"emp": emp, "rubro": _ID_RUBRO_INMOBILIARIA})
    config = config_row.mappings().one()
    servicios = config["servicios"] or {}

    # ── Rendimiento por canal (omnicanal) ─────────────────────────────────────
    channels: list[ChannelBlock] = [
        await provider.get_metrics(db, emp, desde)
        for provider in CHANNEL_PROVIDERS
        if provider.is_enabled(servicios)
    ]

    # ── Summary (KPIs globales, independientes de canal) ─────────────────────
    kpi_row = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM leads
             WHERE id_empresa = :emp AND created_at >= :desde)            AS leads_periodo,
            (SELECT COUNT(*) FROM leads
             WHERE id_empresa = :emp AND estado = 'nuevo'
               AND created_at >= :desde)                                  AS leads_nuevos,
            (SELECT COUNT(*) FROM premium_chat_logs
             WHERE id_empresa = :emp AND created_at >= :desde)            AS consultas_periodo,
            (SELECT COUNT(*) FROM items
             WHERE id_empresa = :emp AND activo = true)                   AS propiedades_activas
    """), {"emp": emp, "desde": desde})
    kpi = kpi_row.mappings().one()

    summary = Summary(
        **dict(kpi),
        canales_activos=len(channels),
        canales_disponibles=len(CHANNEL_PROVIDERS),
    )

    # ── Leads del período (últimos 15 dentro del rango seleccionado) ─────────
    leads_rows = await db.execute(text("""
        SELECT id_lead, nombre, telefono, estado, COALESCE(canal, 'web') AS canal, metadata, created_at
        FROM leads
        WHERE id_empresa = :emp
          AND created_at >= :desde
        ORDER BY created_at DESC
        LIMIT 15
    """), {"emp": emp, "desde": desde})
    leads_raw = leads_rows.mappings().all()

    # Enriquecer con título de propiedad desde metadata['propiedades_interes']
    # Soporta formato UUID string y formato objeto {"id": "...", "titulo": "..."}
    item_ids: list[str] = []
    lead_item_map: dict[int, str] = {}
    lead_titulo_map: dict[int, str] = {}

    for row in leads_raw:
        meta = row["metadata"] or {}
        props = meta.get("propiedades_interes", [])
        if not props:
            continue
        first = props[0]
        if isinstance(first, dict):
            titulo_inline = first.get("titulo")
            if titulo_inline:
                lead_titulo_map[row["id_lead"]] = titulo_inline
                continue
            first_id = str(first.get("id") or first.get("id_item") or "")
        else:
            first_id = str(first)
        if first_id:
            item_ids.append(first_id)
            lead_item_map[row["id_lead"]] = first_id

    titulos_lookup: dict[str, str] = {}
    if item_ids:
        items_rows = await db.execute(text("""
            SELECT id_item::text, titulo
            FROM items
            WHERE id_item = ANY(:ids) AND id_empresa = :emp
        """), {"ids": item_ids, "emp": emp})
        titulos_lookup = {r["id_item"]: r["titulo"] for r in items_rows.mappings()}

    leads_recientes: list[LeadResumen] = [
        LeadResumen(
            fecha            = r["created_at"].isoformat(),
            nombre           = r["nombre"],
            telefono         = r["telefono"],
            propiedad_titulo = (
                lead_titulo_map.get(r["id_lead"])
                or titulos_lookup.get(lead_item_map.get(r["id_lead"], ""))
                or None
            ),
            estado           = r["estado"],
            canal            = r["canal"],
        )
        for r in leads_raw
    ]

    # ── Actividad global (todas las conversaciones, sin distinción de canal) ──
    _dias_periodo = (datetime.now(timezone.utc) - desde).days or 1
    act_row = await db.execute(text("""
        SELECT
            COUNT(*)::int                                                    AS conversaciones_periodo,
            ROUND(COUNT(*) / GREATEST((:dias)::numeric, 1), 1)::float      AS promedio_diario
        FROM premium_chat_logs
        WHERE id_empresa = :emp
          AND created_at >= :desde
    """), {"emp": emp, "desde": desde, "dias": _dias_periodo})
    act = act_row.mappings().one()
    actividad = Actividad(**dict(act))

    # ── Propiedades con más leads ──────────────────────────────────────────────
    # Extrae IDs/títulos desde leads.metadata->propiedades_interes (JSONB)
    # jsonb_array_elements con CASE para tolerar campos NULL o no-array
    leads_props_rows = await db.execute(text("""
        SELECT
            (prop->>'id')      AS id_item_str,
            prop->>'titulo'    AS titulo_fallback,
            COUNT(*)           AS leads_periodo
        FROM leads,
             LATERAL jsonb_array_elements(
                 CASE WHEN jsonb_typeof(metadata->'propiedades_interes') = 'array'
                      THEN metadata->'propiedades_interes'
                      ELSE '[]'::jsonb
                 END
             ) AS prop
        WHERE id_empresa = :emp
          AND created_at >= :desde
          AND (prop->>'id') IS NOT NULL
        GROUP BY (prop->>'id'), prop->>'titulo'
        ORDER BY leads_periodo DESC
        LIMIT 20
    """), {"emp": emp, "desde": desde})
    leads_props_raw = leads_props_rows.mappings().all()

    # Resolver UUIDs contra items para obtener external_id y atributos
    leads_prop_ids = [r["id_item_str"] for r in leads_props_raw if r["id_item_str"] and len(r["id_item_str"]) <= 36]
    items_for_leads: dict[str, dict] = {}
    if leads_prop_ids:
        resolved = await db.execute(text("""
            SELECT id_item::text, external_id, titulo, atributos
            FROM items
            WHERE id_item = ANY(:ids) AND id_empresa = :emp
        """), {"ids": leads_prop_ids, "emp": emp})
        items_for_leads = {r["id_item"]: dict(r) for r in resolved.mappings()}

    # IDs con leads (para excluirlos de consultadas)
    ids_con_leads: set[str] = set(leads_prop_ids)

    props_con_leads: list[PropConLeads] = []
    for r in leads_props_raw:
        id_str = r["id_item_str"] or ""
        item   = items_for_leads.get(id_str)
        if item:
            external_id = item["external_id"]
            titulo      = item["titulo"]
            ubicacion   = _ubicacion(item.get("atributos"))
        else:
            # Fallback: sin resolución en items (propiedad eliminada o UUID inválido)
            external_id = "—"
            titulo      = r["titulo_fallback"] or "Propiedad sin título"
            ubicacion   = None
        props_con_leads.append(PropConLeads(
            external_id   = external_id,
            titulo        = titulo,
            ubicacion     = ubicacion,
            leads_periodo = int(r["leads_periodo"]),
        ))
    props_con_leads = props_con_leads[:10]

    # ── Propiedades consultadas sin lead ──────────────────────────────────────
    # Usa premium_chat_log_items (FK directa a items) donde id_lead IS NULL
    consultadas_rows = await db.execute(text("""
        SELECT
            i.id_item::text   AS id_item,
            i.external_id,
            i.titulo,
            i.atributos,
            COUNT(*)          AS consultas_periodo
        FROM premium_chat_log_items pcli
        JOIN premium_chat_logs pcl ON pcl.id = pcli.id_chat_log
        JOIN items i ON i.id_item = pcli.id_item AND i.id_empresa = :emp
        WHERE pcl.id_empresa  = :emp
          AND pcl.id_lead      IS NULL
          AND pcl.created_at  >= :desde
        GROUP BY i.id_item, i.external_id, i.titulo, i.atributos
        ORDER BY consultas_periodo DESC
        LIMIT 20
    """), {"emp": emp, "desde": desde})

    props_consultadas: list[PropConsultada] = [
        PropConsultada(
            external_id       = r["external_id"],
            titulo            = r["titulo"],
            ubicacion         = _ubicacion(r["atributos"]),
            consultas_periodo = int(r["consultas_periodo"]),
        )
        for r in consultadas_rows.mappings()
        if r["id_item"] not in ids_con_leads   # excluir las que ya tienen leads
    ][:10]

    rankings = Rankings(
        props_con_leads=props_con_leads,
        props_consultadas=props_consultadas,
    )

    # ── Alertas ────────────────────────────────────────────────────────────────
    alertas: list[AlertaCliente] = []

    if int(kpi["propiedades_activas"]) == 0:
        alertas.append(AlertaCliente(
            tipo    = "sin_propiedades",
            mensaje = "No tenés propiedades activas publicadas",
        ))
    if int(kpi["leads_periodo"]) == 0:
        alertas.append(AlertaCliente(
            tipo    = "sin_leads",
            mensaje = "No recibiste leads en este período",
        ))
    notif = config["notificaciones"] or {}
    if not notif.get("telegram", {}).get("enabled") and not notif.get("email", {}).get("enabled"):
        alertas.append(AlertaCliente(
            tipo    = "sin_notificaciones",
            mensaje = "No tenés notificaciones configuradas",
        ))
    if config["github_repo"] is None:
        alertas.append(AlertaCliente(
            tipo    = "sin_catalogo",
            mensaje = "Tu catálogo no está publicado",
        ))

    return ClienteDashboardResponse(
        empresa_nombre  = config["nombre"],
        periodo         = periodo,
        generado_en     = datetime.now(timezone.utc).isoformat(),
        summary         = summary,
        channels        = channels,
        leads_recientes = leads_recientes,
        actividad       = actividad,
        rankings        = rankings,
        alertas         = alertas,
    )
