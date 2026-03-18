"""
FollowupsRepository — acceso a la tabla followups.
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Followup


class FollowupsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        id_lead: int,
        tipo: str,
        fecha_programada: datetime,
        id_conversacion: int | None = None,
        payload: dict | None = None,
    ) -> Followup:
        raise NotImplementedError

    async def get_pending(self, id_empresa: int) -> list[Followup]:
        raise NotImplementedError

    async def update_estado(self, id_followup: int, estado: str, fecha_ejecucion: datetime | None = None) -> None:
        raise NotImplementedError
