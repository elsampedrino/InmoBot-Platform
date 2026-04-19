"""
cliente_dashboard.py — Dashboard para el usuario cliente (inmobiliaria).

Ruta: GET /cliente/dashboard

Devuelve en una sola llamada:
  - KPIs del mes (leads, conversaciones, propiedades activas, tokens*)
  - Leads recientes (últimos 15, enriquecidos con título de propiedad)
  - Actividad del bot (conversaciones del mes + promedio diario)
  - Propiedades publicadas (max 30)
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
    tokens_mes: int  # disponible en backend, UI cliente no lo muestra


class LeadResumen(BaseModel):
    fecha: str
    nombre: str | None
    telefono: str | None
    propiedad_titulo: str | None
    estado: str


class ActividadBot(BaseModel):
    conversaciones_mes: int
    promedio_diario: float


class PropiedadResumen(BaseModel):
    id_item: str
    titulo: str
    tipo: str
    categoria: str
    activo: bool
    destacado: bool


class AlertaCliente(BaseModel):
    tipo: str
    mensaje: str


class ClienteDashboardResponse(BaseModel):
    empresa_nombre: str
    kpis: ClienteKPIs
    leads_recientes: list[LeadResumen]
    actividad_bot: ActividadBot
    propiedades: list[PropiedadResumen]
    alertas: list[AlertaCliente]
    generado_en: str


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
    item_ids: list[str] = []
    lead_item_map: dict[int, str] = {}
    for row in leads_raw:
        meta = row["metadata"] or {}
        props = meta.get("propiedades_interes", [])
        if props:
            first_id = str(props[0])
            item_ids.append(first_id)
            lead_item_map[row["id_lead"]] = first_id

    titulos: dict[str, str] = {}
    if item_ids:
        items_rows = await db.execute(text("""
            SELECT id_item::text, titulo
            FROM items
            WHERE id_item = ANY(:ids) AND id_empresa = :emp
        """), {"ids": item_ids, "emp": emp})
        titulos = {r["id_item"]: r["titulo"] for r in items_rows.mappings()}

    leads_recientes: list[LeadResumen] = [
        LeadResumen(
            fecha            = r["created_at"].isoformat(),
            nombre           = r["nombre"],
            telefono         = r["telefono"],
            propiedad_titulo = titulos.get(lead_item_map.get(r["id_lead"], "")) or None,
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

    # ── Propiedades ────────────────────────────────────────────────────────────
    props_rows = await db.execute(text("""
        SELECT id_item::text, titulo, tipo, categoria, activo, destacado
        FROM items
        WHERE id_empresa = :emp AND id_rubro = :rubro
        ORDER BY destacado DESC, activo DESC, created_at DESC
        LIMIT 30
    """), {"emp": emp, "rubro": _ID_RUBRO_INMOBILIARIA})

    propiedades: list[PropiedadResumen] = [
        PropiedadResumen(
            id_item   = r["id_item"],
            titulo    = r["titulo"],
            tipo      = r["tipo"] or "",
            categoria = r["categoria"] or "",
            activo    = r["activo"],
            destacado = r["destacado"],
        )
        for r in props_rows.mappings()
    ]

    # ── Empresa nombre + config alertas (una query) ────────────────────────────
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
        empresa_nombre     = config["nombre"],
        kpis               = ClienteKPIs(**dict(kpi)),
        leads_recientes    = leads_recientes,
        actividad_bot      = ActividadBot(**dict(act)),
        propiedades        = propiedades,
        alertas            = alertas,
        generado_en        = datetime.now(timezone.utc).isoformat(),
    )
