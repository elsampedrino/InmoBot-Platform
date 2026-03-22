"""
AnalyticsRepository — acceso a premium_chat_logs y premium_conversion_logs.

Estrategia:
  - Inserts vía ORM (add / flush).
  - Lecturas paginadas vía ORM select.
  - get_summary_stats vía SQL raw para agregaciones eficientes.

Schema existente (no figura en DDL original):
  premium_chat_logs     → PK bigint `id`, columnas: id_rubro, consulta, success,
                          model, items_mostrados, etc.
  premium_chat_log_items → PK compuesta (id_chat_log, id_item), campo `rank`
  premium_conversion_logs → PK bigint `id`, event_type, payload
  premium_conversion_log_items → PK compuesta (id_conversion_log, id_item)
"""
from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.db_models import (
    Lead,
    PremiumChatLog,
    PremiumChatLogItem,
    PremiumConversionLog,
    PremiumConversionLogItem,
)

logger = get_logger(__name__)


class AnalyticsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ─── Chat logs ────────────────────────────────────────────────────────────

    async def create_chat_log(self, data: dict) -> PremiumChatLog:
        """
        Inserta una fila en premium_chat_logs.

        Campos requeridos en `data`: id_empresa, id_rubro, canal, consulta.
        Opcionales: id_conversacion, id_lead, session_id, success, error_type,
                    response_time_ms, model, tokens_input, tokens_output,
                    tokens_total, items_mostrados, repo.
        """
        log = PremiumChatLog(
            id_empresa=data["id_empresa"],
            id_rubro=data["id_rubro"],
            id_conversacion=data.get("id_conversacion"),
            id_lead=data.get("id_lead"),
            canal=data["canal"],
            session_id=data.get("session_id"),
            consulta=data.get("consulta", ""),
            idioma=data.get("idioma"),
            success=data.get("success", True),
            error_type=data.get("error_type"),
            response_time_ms=data.get("response_time_ms"),
            model=data.get("model"),
            tokens_input=data.get("tokens_input"),
            tokens_output=data.get("tokens_output"),
            tokens_total=data.get("tokens_total"),
            items_mostrados=data.get("items_mostrados", 0),
            repo=data.get("repo"),
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def create_chat_log_items(self, id_chat_log: int, items_ids: list[str]) -> None:
        """Inserta los items mostrados en premium_chat_log_items."""
        if not items_ids:
            return
        import uuid as _uuid
        items = [
            PremiumChatLogItem(
                id_chat_log=id_chat_log,
                id_item=_uuid.UUID(item_id),
                rank=pos,
            )
            for pos, item_id in enumerate(items_ids)
        ]
        self.db.add_all(items)
        await self.db.flush()

    # ─── Conversion logs ──────────────────────────────────────────────────────

    async def create_conversion_log(self, data: dict) -> PremiumConversionLog:
        """
        Inserta una fila en premium_conversion_logs.

        Campos requeridos en `data`: id_empresa, id_rubro, canal, event_type.
        Opcionales: id_conversacion, id_lead, session_id, payload, repo.
        """
        log = PremiumConversionLog(
            id_empresa=data["id_empresa"],
            id_rubro=data["id_rubro"],
            id_conversacion=data.get("id_conversacion"),
            id_lead=data.get("id_lead"),
            canal=data["canal"],
            session_id=data.get("session_id"),
            event_type=data["event_type"],
            payload=data.get("payload") or {},
            repo=data.get("repo"),
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def create_conversion_log_items(
        self, id_conversion_log: int, items_ids: list[str]
    ) -> None:
        """Inserta los items asociados al evento de conversión."""
        if not items_ids:
            return
        import uuid as _uuid
        items = [
            PremiumConversionLogItem(
                id_conversion_log=id_conversion_log,
                id_item=_uuid.UUID(item_id),
            )
            for item_id in items_ids
        ]
        self.db.add_all(items)
        await self.db.flush()

    # ─── Lecturas paginadas ───────────────────────────────────────────────────

    async def get_chat_logs(
        self, id_empresa: int, offset: int, limit: int
    ) -> tuple[list[PremiumChatLog], int]:
        count_stmt = select(func.count()).select_from(PremiumChatLog).where(
            PremiumChatLog.id_empresa == id_empresa
        )
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(PremiumChatLog)
            .where(PremiumChatLog.id_empresa == id_empresa)
            .order_by(PremiumChatLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        logs = list(result.scalars().all())
        return logs, total

    async def get_conversion_logs(
        self, id_empresa: int, evento: str | None, offset: int, limit: int
    ) -> tuple[list[PremiumConversionLog], int]:
        base_where = PremiumConversionLog.id_empresa == id_empresa
        count_stmt = select(func.count()).select_from(PremiumConversionLog).where(base_where)
        stmt = select(PremiumConversionLog).where(base_where)

        if evento:
            count_stmt = count_stmt.where(PremiumConversionLog.event_type == evento)
            stmt = stmt.where(PremiumConversionLog.event_type == evento)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(PremiumConversionLog.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        logs = list(result.scalars().all())
        return logs, total

    # ─── Agregaciones ─────────────────────────────────────────────────────────

    async def get_summary_stats(self, id_empresa: int, desde: datetime) -> dict:
        """Devuelve stats agregadas del período usando SQL raw para eficiencia."""
        row = (await self.db.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM premium_chat_logs
                 WHERE id_empresa = :id_empresa AND created_at >= :desde)      AS total_chats,
                (SELECT COUNT(*) FROM premium_conversion_logs
                 WHERE id_empresa = :id_empresa AND created_at >= :desde)      AS total_conversiones,
                (SELECT COUNT(*) FROM leads
                 WHERE id_empresa = :id_empresa AND created_at >= :desde)      AS total_leads,
                (SELECT AVG(response_time_ms) FROM premium_chat_logs
                 WHERE id_empresa = :id_empresa AND created_at >= :desde)      AS avg_response_time_ms
        """), {"id_empresa": id_empresa, "desde": desde})).mappings().first()

        # Distribución por modelo usado (proxy de rutas)
        model_rows = (await self.db.execute(text("""
            SELECT model, COUNT(*) AS cnt
            FROM premium_chat_logs
            WHERE id_empresa = :id_empresa AND created_at >= :desde
            GROUP BY model
        """), {"id_empresa": id_empresa, "desde": desde})).mappings().all()

        # Distribución de event_type de conversión
        events_rows = (await self.db.execute(text("""
            SELECT event_type, COUNT(*) AS cnt
            FROM premium_conversion_logs
            WHERE id_empresa = :id_empresa AND created_at >= :desde
            GROUP BY event_type
        """), {"id_empresa": id_empresa, "desde": desde})).mappings().all()

        return {
            "total_chats": int(row["total_chats"] or 0),
            "total_conversiones": int(row["total_conversiones"] or 0),
            "total_leads": int(row["total_leads"] or 0),
            "avg_response_time_ms": (
                float(row["avg_response_time_ms"])
                if row["avg_response_time_ms"] is not None
                else None
            ),
            "routes_distribution": {
                r["model"] or "deterministic": int(r["cnt"])
                for r in model_rows
            },
            "conversion_events_distribution": {
                r["event_type"]: int(r["cnt"])
                for r in events_rows
            },
        }
