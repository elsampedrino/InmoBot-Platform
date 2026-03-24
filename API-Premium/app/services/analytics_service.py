"""
AnalyticsService — registro de eventos de chat y conversión.

Responsabilidades:
- Registrar cada turno en premium_chat_logs + premium_chat_log_items
- Registrar eventos de conversión en premium_conversion_logs
- Exponer métricas agregadas para el dashboard

No debe:
- Tomar decisiones conversacionales
- Depender del canal específico
- Modificar la lógica principal del turno
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.api_models import AnalyticsSummaryResponse, ChatLogResponse, ConversionLogResponse
from app.models.domain_models import ConversionEvent, RouterDecision
from app.repositories.analytics_repository import AnalyticsRepository

logger = get_logger(__name__)


def _fmt_dt(dt) -> str:
    """Formatea datetime a ISO string."""
    if dt is None:
        return ""
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = AnalyticsRepository(db)

    async def log_chat_turn(
        self,
        id_empresa: int,
        id_rubro: int,
        id_conversacion: int | None,
        id_lead: int | None,
        session_id: str,
        canal: str,
        consulta: str,
        decision: RouterDecision,
        model_usado: str,
        tokens_input: int,
        tokens_output: int,
        response_time_ms: int,
        items_ids: list[str],
    ) -> int:
        """
        Registra el turno completo en premium_chat_logs.
        Devuelve el id (bigint) del log generado.
        """
        data = {
            "id_empresa": id_empresa,
            "id_rubro": id_rubro,
            "id_conversacion": id_conversacion,
            "id_lead": id_lead,
            "canal": canal,
            "session_id": session_id,
            "consulta": consulta,
            "success": True,
            "model": model_usado,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "tokens_total": tokens_input + tokens_output,
            "response_time_ms": response_time_ms,
            "items_mostrados": len(items_ids),
        }
        log = await self._repo.create_chat_log(data)

        if items_ids:
            await self._repo.create_chat_log_items(log.id, items_ids)

        logger.debug(
            "chat_turn_logged",
            id_log=log.id,
            model=model_usado,
            items_count=len(items_ids),
        )
        return log.id

    async def log_conversion_event(
        self,
        id_empresa: int,
        id_rubro: int,
        canal: str,
        evento: ConversionEvent,
        id_conversacion: int | None = None,
        id_lead: int | None = None,
        session_id: str | None = None,
        items_ids: list[str] | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Registra un evento de conversión en premium_conversion_logs.
        Usa savepoint para que un fallo de constraint no corrompa la sesión principal.
        """
        data = {
            "id_empresa": id_empresa,
            "id_rubro": id_rubro,
            "id_conversacion": id_conversacion,
            "id_lead": id_lead,
            "canal": canal,
            "session_id": session_id,
            "event_type": evento.value,
            "payload": metadata or {},
        }
        # Savepoint: si el INSERT falla (ej. constraint violation), solo se
        # deshace esta operación sin dejar la sesión en estado PendingRollback.
        async with self._repo.db.begin_nested():
            log = await self._repo.create_conversion_log(data)
            if items_ids:
                await self._repo.create_conversion_log_items(log.id, items_ids)

        logger.info(
            "conversion_event_logged",
            evento=evento.value,
            id_lead=id_lead,
            id_conversacion=id_conversacion,
        )

    async def get_summary(self, id_empresa: int, dias: int) -> AnalyticsSummaryResponse:
        """Métricas agregadas del período."""
        desde = datetime.now(timezone.utc) - timedelta(days=dias)
        stats = await self._repo.get_summary_stats(id_empresa=id_empresa, desde=desde)

        return AnalyticsSummaryResponse(
            total_chats=stats["total_chats"],
            total_conversiones=stats["total_conversiones"],
            total_leads=stats["total_leads"],
            routes_distribution=stats["routes_distribution"],
            conversion_events_distribution=stats["conversion_events_distribution"],
            avg_response_time_ms=stats["avg_response_time_ms"],
            periodo=f"últimos {dias} días",
        )

    async def get_chat_logs(
        self, id_empresa: int, page: int, page_size: int
    ) -> list[ChatLogResponse]:
        """Lista paginada de logs de chat."""
        offset = (page - 1) * page_size
        logs, _ = await self._repo.get_chat_logs(
            id_empresa=id_empresa, offset=offset, limit=page_size
        )
        return [
            ChatLogResponse(
                id_log=str(log.id),
                id_empresa=log.id_empresa,
                session_id=log.session_id,
                canal=log.canal,
                consulta=log.consulta,
                success=log.success,
                model=log.model,
                tokens_input=log.tokens_input,
                tokens_output=log.tokens_output,
                response_time_ms=log.response_time_ms,
                items_mostrados=log.items_mostrados,
                created_at=_fmt_dt(log.created_at),
            )
            for log in logs
        ]

    async def get_conversion_logs(
        self, id_empresa: int, evento: str | None, page: int, page_size: int
    ) -> list[ConversionLogResponse]:
        """Lista paginada de eventos de conversión."""
        offset = (page - 1) * page_size
        logs, _ = await self._repo.get_conversion_logs(
            id_empresa=id_empresa, evento=evento, offset=offset, limit=page_size
        )
        return [
            ConversionLogResponse(
                id_conversion=str(log.id),
                id_empresa=log.id_empresa,
                id_lead=log.id_lead,
                event_type=log.event_type,
                payload=log.payload or {},
                created_at=_fmt_dt(log.created_at),
            )
            for log in logs
        ]
