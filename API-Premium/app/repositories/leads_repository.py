"""
LeadsRepository — acceso a la tabla leads.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Lead


class LeadsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        id_empresa: int,
        canal: str | None,
        nombre: str | None = None,
        telefono: str | None = None,
        email: str | None = None,
        metadata: dict | None = None,
    ) -> Lead:
        raise NotImplementedError

    async def get_by_id(self, id_lead: int) -> Lead | None:
        raise NotImplementedError

    async def update(self, id_lead: int, data: dict) -> Lead:
        raise NotImplementedError

    async def list_by_empresa(
        self,
        id_empresa: int,
        estado: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Lead], int]:
        raise NotImplementedError
