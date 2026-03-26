"""
LeadsRepository — acceso a la tabla leads.

Estrategia:
  - CRUD sobre ORM SQLAlchemy (select / add / flush).
  - list_by_empresa: paginación con count separado para evitar subquery costosa.
  - update: actualiza solo las claves presentes en el dict `data`.
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.db_models import Lead

logger = get_logger(__name__)


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
        lead = Lead(
            id_empresa=id_empresa,
            canal=canal,
            nombre=nombre,
            telefono=telefono,
            email=email,
            metadata_=metadata or {},
            estado="nuevo",
        )
        self.db.add(lead)
        await self.db.flush()  # genera id_lead sin commit
        logger.info(
            "lead_created",
            id_lead=lead.id_lead,
            id_empresa=id_empresa,
            canal=canal,
        )
        return lead

    async def get_by_id(self, id_lead: int) -> Lead | None:
        result = await self.db.execute(
            select(Lead).where(Lead.id_lead == id_lead)
        )
        return result.scalar_one_or_none()

    async def update(self, id_lead: int, data: dict) -> Lead:
        """
        Actualiza los campos del lead. `data` usa nombres de atributos Python
        (ej: metadata_ para el campo 'metadata', nombre para 'nombre').
        Solo actualiza las claves presentes; ignora las ausentes.
        """
        lead = await self.get_by_id(id_lead)
        if lead is None:
            raise ValueError(f"Lead {id_lead} no encontrado")

        for attr, value in data.items():
            setattr(lead, attr, value)

        await self.db.flush()
        logger.info("lead_updated", id_lead=id_lead, campos=list(data.keys()))
        return lead

    async def list_by_empresa(
        self,
        id_empresa: int,
        estado: str | None,
        offset: int,
        limit: int,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> tuple[list[Lead], int]:
        base = select(Lead).where(Lead.id_empresa == id_empresa)
        if estado:
            base = base.where(Lead.estado == estado)
        if fecha_desde:
            base = base.where(Lead.created_at >= fecha_desde)
        if fecha_hasta:
            base = base.where(Lead.created_at <= fecha_hasta)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        leads = list(result.scalars().all())

        return leads, total

    async def get_by_id_empresa(self, id_lead: int, id_empresa: int) -> Lead | None:
        result = await self.db.execute(
            select(Lead).where(Lead.id_lead == id_lead, Lead.id_empresa == id_empresa)
        )
        return result.scalar_one_or_none()
