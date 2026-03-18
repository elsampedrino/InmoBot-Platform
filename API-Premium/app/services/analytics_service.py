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
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_models import AnalyticsSummaryResponse, ChatLogResponse, ConversionLogResponse
from app.models.domain_models import ConversionEvent, RouterDecision


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log_chat_turn(
        self,
        id_empresa: int,
        id_conversacion: int | None,
        session_id: str,
        canal: str,
        decision: RouterDecision,
        model_usado: str,
        tokens_input: int,
        tokens_output: int,
        response_time_ms: int,
        items_ids: list[str],
    ) -> uuid.UUID:
        """
        Registra el turno completo en premium_chat_logs.
        Devuelve el id_log generado.
        """
        # TODO Fase 6
        raise NotImplementedError

    async def log_conversion_event(
        self,
        id_empresa: int,
        evento: ConversionEvent,
        id_conversacion: int | None = None,
        id_lead: int | None = None,
        route: str | None = None,
        items_ids: list[str] | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Registra un evento de conversión en premium_conversion_logs."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_summary(self, id_empresa: int, dias: int) -> AnalyticsSummaryResponse:
        """Métricas agregadas del período."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_chat_logs(
        self, id_empresa: int, page: int, page_size: int
    ) -> list[ChatLogResponse]:
        """Lista paginada de logs de chat."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_conversion_logs(
        self, id_empresa: int, evento: str | None, page: int, page_size: int
    ) -> list[ConversionLogResponse]:
        """Lista paginada de eventos de conversión."""
        # TODO Fase 6
        raise NotImplementedError
