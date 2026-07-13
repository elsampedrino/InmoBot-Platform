"""
channel_metrics.py — Proveedores de métricas por canal de atención.

Cada canal (web, whatsapp, futuro instagram/messenger/telegram) implementa
ChannelProvider de forma autocontenida: decide si está habilitado para una
empresa (is_enabled) y calcula sus propias métricas (get_metrics). El
dashboard cliente solo itera CHANNEL_PROVIDERS — agregar un canal nuevo
significa escribir una clase nueva y sumarla a la lista, sin tocar el
endpoint ni el frontend (que renderiza ChannelBlock genéricamente).
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ChannelMetric(BaseModel):
    key: str
    label: str
    value: float
    format: Literal["int", "percent", "currency"] = "int"
    sub: str | None = None


class ChannelBlock(BaseModel):
    type: str
    label: str
    icon: str
    metrics: list[ChannelMetric]


class ChannelProvider(ABC):
    type: str
    label: str
    icon: str

    @abstractmethod
    def is_enabled(self, servicios: dict) -> bool: ...

    @abstractmethod
    async def get_metrics(self, db: AsyncSession, id_empresa: int, desde: datetime) -> ChannelBlock: ...


class WebChannelProvider(ChannelProvider):
    """Widget web embebido en la landing. Es el canal base: habilitado por
    defecto salvo que la empresa lo desactive explícitamente (servicios.canal_web=false)."""

    type  = "web"
    label = "Widget Web"
    icon  = "web"

    def is_enabled(self, servicios: dict) -> bool:
        return servicios.get("canal_web", True)

    async def get_metrics(self, db: AsyncSession, id_empresa: int, desde: datetime) -> ChannelBlock:
        row = await db.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM premium_chat_logs
                 WHERE id_empresa = :emp AND COALESCE(canal, 'web') = 'web'
                   AND created_at >= :desde)                                AS consultas,
                (SELECT COUNT(*) FROM leads
                 WHERE id_empresa = :emp AND COALESCE(canal, 'web') = 'web'
                   AND created_at >= :desde)                                AS leads
        """), {"emp": id_empresa, "desde": desde})
        r = row.mappings().one()
        consultas  = int(r["consultas"])
        leads      = int(r["leads"])
        conversion = round(leads / consultas * 100, 1) if consultas > 0 else 0.0

        return ChannelBlock(
            type=self.type, label=self.label, icon=self.icon,
            metrics=[
                ChannelMetric(key="consultas",  label="Consultas",       value=consultas,  format="int"),
                ChannelMetric(key="leads",      label="Leads generados", value=leads,      format="int"),
                ChannelMetric(key="conversion", label="Conversión",      value=conversion, format="percent"),
            ],
        )


class WhatsAppChannelProvider(ChannelProvider):
    type  = "whatsapp"
    label = "WhatsApp"
    icon  = "whatsapp"

    def is_enabled(self, servicios: dict) -> bool:
        return servicios.get("canal_whatsapp", False)

    async def get_metrics(self, db: AsyncSession, id_empresa: int, desde: datetime) -> ChannelBlock:
        row = await db.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM premium_chat_logs
                 WHERE id_empresa = :emp AND canal = 'whatsapp'
                   AND created_at >= :desde)                                      AS consultas,
                (SELECT COUNT(*) FROM premium_conversion_logs
                 WHERE id_empresa = :emp AND event_type = 'whatsapp_bot_after_hours'
                   AND created_at >= :desde)                                      AS ia_respondio,
                (SELECT COUNT(*) FROM premium_conversion_logs
                 WHERE id_empresa = :emp AND event_type = 'whatsapp_handoff_business_hours'
                   AND created_at >= :desde)                                      AS derivadas_humano,
                (SELECT COUNT(*) FROM leads
                 WHERE id_empresa = :emp AND canal = 'whatsapp'
                   AND created_at >= :desde)                                      AS leads
        """), {"emp": id_empresa, "desde": desde})
        r = row.mappings().one()
        ia        = int(r["ia_respondio"])
        humano    = int(r["derivadas_humano"])
        total     = ia + humano
        pct_autom = round(ia / total * 100, 1) if total > 0 else 0.0

        return ChannelBlock(
            type=self.type, label=self.label, icon=self.icon,
            metrics=[
                ChannelMetric(key="consultas",       label="Consultas",          value=int(r["consultas"]), format="int"),
                ChannelMetric(key="ia_respondio",     label="IA respondió",       value=ia,                  format="int"),
                ChannelMetric(key="derivadas_humano", label="Derivadas a humano", value=humano,               format="int"),
                ChannelMetric(key="automatizacion",   label="% Automatización",   value=pct_autom,            format="percent", sub="IA / (IA + Humano)"),
                ChannelMetric(key="leads",            label="Leads",              value=int(r["leads"]),      format="int"),
            ],
        )


# Registro de canales soportados por la plataforma. Para sumar un canal nuevo
# (Instagram DM, Messenger, Telegram...): escribir su ChannelProvider y agregarlo
# acá. No requiere cambios en cliente_dashboard.py ni en el frontend.
CHANNEL_PROVIDERS: list[ChannelProvider] = [
    WebChannelProvider(),
    WhatsAppChannelProvider(),
]
