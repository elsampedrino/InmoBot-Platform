"""
AnalyticsRepository — acceso a premium_chat_logs y premium_conversion_logs.
"""
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import PremiumChatLog, PremiumConversionLog


class AnalyticsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_chat_log(self, data: dict) -> PremiumChatLog:
        raise NotImplementedError

    async def create_chat_log_items(self, id_log: uuid.UUID, items_ids: list[str]) -> None:
        raise NotImplementedError

    async def create_conversion_log(self, data: dict) -> PremiumConversionLog:
        raise NotImplementedError

    async def create_conversion_log_items(
        self, id_conversion: uuid.UUID, items_ids: list[str]
    ) -> None:
        raise NotImplementedError

    async def get_chat_logs(
        self, id_empresa: int, offset: int, limit: int
    ) -> tuple[list[PremiumChatLog], int]:
        raise NotImplementedError

    async def get_conversion_logs(
        self, id_empresa: int, evento: str | None, offset: int, limit: int
    ) -> tuple[list[PremiumConversionLog], int]:
        raise NotImplementedError

    async def get_summary_stats(
        self, id_empresa: int, desde: datetime
    ) -> dict:
        """Devuelve stats agregadas: total_chats, conversiones, routes_dist, etc."""
        raise NotImplementedError
