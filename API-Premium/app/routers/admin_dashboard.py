"""
admin_dashboard.py — Dashboard operativo para el superadmin.

Ruta: GET /admin/dashboard

Devuelve en una sola llamada:
  - KPIs globales del mes
  - Uso por empresa (tokens, leads, importaciones, costo estimado)
  - Actividad reciente (importacion_logs)
  - Alertas operativas simples
"""
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin

router = APIRouter()

# ─── Umbrales de consumo (v1 — provisionales, ajustar con histórico real) ─────
_UMBRAL_ALTO     = 100_000   # tokens/mes
_UMBRAL_CRITICO  = 500_000   # tokens/mes

# Precios Sonnet (USD por token)
_PRECIO_INPUT_POR_TOKEN  = 3.0  / 1_000_000
_PRECIO_OUTPUT_POR_TOKEN = 15.0 / 1_000_000


# ─── Modelos de respuesta ─────────────────────────────────────────────────────

class DashboardKPIs(BaseModel):
    empresas_activas: int
    usuarios_activos: int
    importaciones_mes: int
    publicaciones_mes: int
    tokens_mes: int


class EmpresaUso(BaseModel):
    id_empresa: int
    nombre: str
    plan: str | None
    importaciones_mes: int
    publicaciones_mes: int
    leads_mes: int
    tokens_mes: int
    tokens_input: int
    tokens_output: int
    costo_usd: float
    estado_consumo: Literal["normal", "alto", "critico"]


class ActividadItem(BaseModel):
    fecha: str
    empresa: str
    accion: str
    resultado: str
    usuario: str | None
    detalle: dict | None


class Alerta(BaseModel):
    tipo: str
    empresa: str
    detalle: str


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    uso_por_empresa: list[EmpresaUso]
    actividad_reciente: list[ActividadItem]
    alertas: list[Alerta]
    generado_en: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _estado_consumo(tokens: int) -> Literal["normal", "alto", "critico"]:
    if tokens >= _UMBRAL_CRITICO:
        return "critico"
    if tokens >= _UMBRAL_ALTO:
        return "alto"
    return "normal"


def _costo(tokens_input: int, tokens_output: int) -> float:
    return round(
        tokens_input  * _PRECIO_INPUT_POR_TOKEN +
        tokens_output * _PRECIO_OUTPUT_POR_TOKEN,
        4,
    )


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    # ── KPIs globales ──────────────────────────────────────────────────────────
    kpi_rows = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM empresas       WHERE activa = true)                          AS empresas_activas,
            (SELECT COUNT(*) FROM usuarios_admin WHERE activo = true)                          AS usuarios_activos,
            (SELECT COUNT(*) FROM importacion_logs
             WHERE accion = 'aplicar_db'      AND created_at >= date_trunc('month', NOW()))    AS importaciones_mes,
            (SELECT COUNT(*) FROM importacion_logs
             WHERE accion = 'publicar_github' AND created_at >= date_trunc('month', NOW()))    AS publicaciones_mes,
            (SELECT COALESCE(SUM(tokens_total), 0) FROM premium_chat_logs
             WHERE created_at >= date_trunc('month', NOW()))                                   AS tokens_mes
    """))
    kpi = kpi_rows.mappings().one()

    # ── Uso por empresa ────────────────────────────────────────────────────────
    uso_rows = await db.execute(text("""
        SELECT
            e.id_empresa,
            e.nombre,
            p.nombre                                           AS plan,
            COALESCE(imp.cnt, 0)                               AS importaciones_mes,
            COALESCE(pub.cnt, 0)                               AS publicaciones_mes,
            COALESCE(lds.cnt, 0)                               AS leads_mes,
            COALESCE(tok.tokens_total, 0)::int                 AS tokens_mes,
            COALESCE(tok.tokens_input,  0)::int                AS tokens_input,
            COALESCE(tok.tokens_output, 0)::int                AS tokens_output,
            -- Alertas: repo configurado y notificaciones
            erc.github_repo,
            e.notificaciones
        FROM empresas e
        LEFT JOIN planes p ON p.id_plan = e.id_plan
        LEFT JOIN (
            SELECT id_empresa, COUNT(*) AS cnt
            FROM importacion_logs
            WHERE accion = 'aplicar_db' AND created_at >= date_trunc('month', NOW())
            GROUP BY id_empresa
        ) imp ON imp.id_empresa = e.id_empresa
        LEFT JOIN (
            SELECT id_empresa, COUNT(*) AS cnt
            FROM importacion_logs
            WHERE accion = 'publicar_github' AND created_at >= date_trunc('month', NOW())
            GROUP BY id_empresa
        ) pub ON pub.id_empresa = e.id_empresa
        LEFT JOIN (
            SELECT id_empresa, COUNT(*) AS cnt
            FROM leads
            WHERE created_at >= date_trunc('month', NOW())
            GROUP BY id_empresa
        ) lds ON lds.id_empresa = e.id_empresa
        LEFT JOIN (
            SELECT id_empresa,
                   SUM(tokens_total)  AS tokens_total,
                   SUM(tokens_input)  AS tokens_input,
                   SUM(tokens_output) AS tokens_output
            FROM premium_chat_logs
            WHERE created_at >= date_trunc('month', NOW())
            GROUP BY id_empresa
        ) tok ON tok.id_empresa = e.id_empresa
        LEFT JOIN empresa_rubro_catalogos erc
               ON erc.id_empresa = e.id_empresa AND erc.id_rubro = 1
        WHERE e.activa = true
        ORDER BY COALESCE(tok.tokens_total, 0) DESC
    """))
    uso_raw = uso_rows.mappings().all()

    uso_por_empresa: list[EmpresaUso] = []
    alertas: list[Alerta] = []

    for r in uso_raw:
        tokens_mes    = int(r["tokens_mes"])
        tokens_input  = int(r["tokens_input"])
        tokens_output = int(r["tokens_output"])
        nombre        = r["nombre"]

        uso_por_empresa.append(EmpresaUso(
            id_empresa        = r["id_empresa"],
            nombre            = nombre,
            plan              = r["plan"],
            importaciones_mes = int(r["importaciones_mes"]),
            publicaciones_mes = int(r["publicaciones_mes"]),
            leads_mes         = int(r["leads_mes"]),
            tokens_mes        = tokens_mes,
            tokens_input      = tokens_input,
            tokens_output     = tokens_output,
            costo_usd         = _costo(tokens_input, tokens_output),
            estado_consumo    = _estado_consumo(tokens_mes),
        ))

        # Alertas por empresa
        notif = r["notificaciones"] or {}
        tg_ok = notif.get("telegram", {}).get("enabled", False)
        em_ok = notif.get("email",    {}).get("enabled", False)
        if not tg_ok and not em_ok:
            alertas.append(Alerta(
                tipo    = "sin_notificaciones",
                empresa = nombre,
                detalle = "Telegram y email desactivados",
            ))

        if r["github_repo"] is None:
            alertas.append(Alerta(
                tipo    = "sin_repo",
                empresa = nombre,
                detalle = "Repo GitHub no configurado",
            ))

        if _estado_consumo(tokens_mes) in ("alto", "critico"):
            alertas.append(Alerta(
                tipo    = _estado_consumo(tokens_mes),
                empresa = nombre,
                detalle = f"{tokens_mes:,} tokens este mes".replace(",", "."),
            ))

    # ── Actividad reciente ─────────────────────────────────────────────────────
    act_rows = await db.execute(text("""
        SELECT
            il.created_at,
            e.nombre  AS empresa,
            il.accion,
            il.resultado,
            il.nombre_usuario,
            il.detalle
        FROM importacion_logs il
        JOIN empresas e ON e.id_empresa = il.id_empresa
        ORDER BY il.created_at DESC
        LIMIT 20
    """))

    actividad: list[ActividadItem] = [
        ActividadItem(
            fecha    = r["created_at"].isoformat(),
            empresa  = r["empresa"],
            accion   = r["accion"],
            resultado= r["resultado"],
            usuario  = r["nombre_usuario"],
            detalle  = dict(r["detalle"]) if r["detalle"] else None,
        )
        for r in act_rows.mappings()
    ]

    return DashboardResponse(
        kpis               = DashboardKPIs(**dict(kpi)),
        uso_por_empresa    = uso_por_empresa,
        actividad_reciente = actividad,
        alertas            = alertas,
        generado_en        = datetime.now(timezone.utc).isoformat(),
    )
