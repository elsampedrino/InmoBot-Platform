"""
cliente_dashboard.py — Dashboard para el usuario cliente (inmobiliaria).

Ruta: GET /cliente/dashboard

Devuelve en una sola llamada:
  - KPIs del mes (leads, conversaciones, propiedades activas, tokens*)
  - Leads recientes (últimos 15, enriquecidos con título de propiedad)
  - Actividad del bot (conversaciones del mes + promedio diario)
  - Propiedades con más leads del mes (top 10)
  - Propiedades más consultadas sin lead del mes (top 10)
  - Alertas simples para el cliente

* tokens_mes calculado en backend pero no expuesto en UI cliente por decisión de producto.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin

router = APIRouter()

# Rubro inmobiliaria — único punto de definición para este módulo
_ID_RUBRO_INMOBILIARIA = 1


# ─── Modelos de respuesta ─────────────────────────────────────────────────────

class ClienteKPIs(BaseModel):
    leads_mes: int
    leads_nuevos: int
    conversaciones_mes: int
    propiedades_activas: int
    tokens_mes: int  # calculado en backend, no expuesto en UI cliente


class LeadResumen(BaseModel):
    fecha: str
    nombre: str | None
    telefono: str | None
    propiedad_titulo: str | None
    estado: str


class ActividadBot(BaseModel):
    conversaciones_mes: int
    promedio_diario: float


class PropConLeads(BaseModel):
    external_id: str        # identificador principal (ej: PROP-001)
    titulo: str
    ubicacion: str | None
    leads_mes: int


class PropConsultada(BaseModel):
    external_id: str
    titulo: str
    ubicacion: str | None
    consultas_mes: int


class AlertaCliente(BaseModel):
    tipo: str
    mensaje: str


class ClienteDashboardResponse(BaseModel):
    empresa_nombre: str
    kpis: ClienteKPIs
    leads_recientes: list[LeadResumen]
    actividad_bot: ActividadBot
    props_con_leads: list[PropConLeads]
    props_consultadas: list[PropConsultada]
    alertas: list[AlertaCliente]
    generado_en: str


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
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    emp = current_user.id_empresa

    # ── KPIs (una sola query) ──────────────────────────────────────────────────
    kpi_row = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM leads
             WHERE id_empresa = :emp
               AND created_at >= date_trunc('month', NOW()))              AS leads_mes,
            (SELECT COUNT(*) FROM leads
             WHERE id_empresa = :emp AND estado = 'nuevo'
               AND created_at >= date_trunc('month', NOW()))              AS leads_nuevos,
            (SELECT COUNT(*) FROM premium_chat_logs
             WHERE id_empresa = :emp
               AND created_at >= date_trunc('month', NOW()))              AS conversaciones_mes,
            (SELECT COUNT(*) FROM items
             WHERE id_empresa = :emp AND activo = true)                   AS propiedades_activas,
            (SELECT COALESCE(SUM(tokens_total), 0) FROM premium_chat_logs
             WHERE id_empresa = :emp
               AND created_at >= date_trunc('month', NOW()))              AS tokens_mes
    """), {"emp": emp})
    kpi = kpi_row.mappings().one()

    # ── Leads recientes ────────────────────────────────────────────────────────
    leads_rows = await db.execute(text("""
        SELECT id_lead, nombre, telefono, estado, metadata, created_at
        FROM leads
        WHERE id_empresa = :emp
        ORDER BY created_at DESC
        LIMIT 15
    """), {"emp": emp})
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
        )
        for r in leads_raw
    ]

    # ── Actividad del bot ──────────────────────────────────────────────────────
    act_row = await db.execute(text("""
        SELECT
            COUNT(*)::int                                                               AS conversaciones_mes,
            ROUND(COUNT(*) / GREATEST(EXTRACT(DAY FROM NOW())::numeric, 1), 1)::float  AS promedio_diario
        FROM premium_chat_logs
        WHERE id_empresa = :emp
          AND created_at >= date_trunc('month', NOW())
    """), {"emp": emp})
    act = act_row.mappings().one()

    # ── Propiedades con más leads ──────────────────────────────────────────────
    # Extrae IDs/títulos desde leads.metadata->propiedades_interes (JSONB)
    # jsonb_array_elements con CASE para tolerar campos NULL o no-array
    leads_props_rows = await db.execute(text("""
        SELECT
            (prop->>'id')      AS id_item_str,
            prop->>'titulo'    AS titulo_fallback,
            COUNT(*)           AS leads_mes
        FROM leads,
             LATERAL jsonb_array_elements(
                 CASE WHEN jsonb_typeof(metadata->'propiedades_interes') = 'array'
                      THEN metadata->'propiedades_interes'
                      ELSE '[]'::jsonb
                 END
             ) AS prop
        WHERE id_empresa = :emp
          AND created_at >= date_trunc('month', NOW())
          AND (prop->>'id') IS NOT NULL
        GROUP BY (prop->>'id'), prop->>'titulo'
        ORDER BY leads_mes DESC
        LIMIT 20
    """), {"emp": emp})
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
            external_id = external_id,
            titulo      = titulo,
            ubicacion   = ubicacion,
            leads_mes   = int(r["leads_mes"]),
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
            COUNT(*)          AS consultas_mes
        FROM premium_chat_log_items pcli
        JOIN premium_chat_logs pcl ON pcl.id = pcli.id_chat_log
        JOIN items i ON i.id_item = pcli.id_item AND i.id_empresa = :emp
        WHERE pcl.id_empresa  = :emp
          AND pcl.id_lead      IS NULL
          AND pcl.created_at  >= date_trunc('month', NOW())
        GROUP BY i.id_item, i.external_id, i.titulo, i.atributos
        ORDER BY consultas_mes DESC
        LIMIT 20
    """), {"emp": emp})

    props_consultadas: list[PropConsultada] = [
        PropConsultada(
            external_id  = r["external_id"],
            titulo       = r["titulo"],
            ubicacion    = _ubicacion(r["atributos"]),
            consultas_mes = int(r["consultas_mes"]),
        )
        for r in consultadas_rows.mappings()
        if r["id_item"] not in ids_con_leads   # excluir las que ya tienen leads
    ][:10]

    # ── Empresa nombre + config alertas ───────────────────────────────────────
    config_row = await db.execute(text("""
        SELECT e.nombre, e.notificaciones, erc.github_repo
        FROM empresas e
        LEFT JOIN empresa_rubro_catalogos erc
               ON erc.id_empresa = e.id_empresa AND erc.id_rubro = :rubro
        WHERE e.id_empresa = :emp
    """), {"emp": emp, "rubro": _ID_RUBRO_INMOBILIARIA})
    config = config_row.mappings().one()

    # ── Alertas ────────────────────────────────────────────────────────────────
    alertas: list[AlertaCliente] = []

    if int(kpi["propiedades_activas"]) == 0:
        alertas.append(AlertaCliente(
            tipo    = "sin_propiedades",
            mensaje = "No tenés propiedades activas publicadas",
        ))
    if int(kpi["leads_mes"]) == 0:
        alertas.append(AlertaCliente(
            tipo    = "sin_leads",
            mensaje = "No recibiste leads este mes",
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
        empresa_nombre    = config["nombre"],
        kpis              = ClienteKPIs(**dict(kpi)),
        leads_recientes   = leads_recientes,
        actividad_bot     = ActividadBot(**dict(act)),
        props_con_leads   = props_con_leads,
        props_consultadas = props_consultadas,
        alertas           = alertas,
        generado_en       = datetime.now(timezone.utc).isoformat(),
    )
