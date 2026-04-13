"""
empresas_repository.py — Operaciones CRUD sobre la tabla empresas.
Usado exclusivamente por admin_empresas.py (panel superadmin).
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Empresa


async def list_empresas(
    db: AsyncSession,
    activa: bool | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Empresa], int]:
    q = select(Empresa)
    if activa is not None:
        q = q.where(Empresa.activa == activa)
    q = q.order_by(Empresa.nombre.asc())

    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar_one()

    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), total


async def get_empresa(db: AsyncSession, id_empresa: int) -> Empresa | None:
    result = await db.execute(select(Empresa).where(Empresa.id_empresa == id_empresa))
    return result.scalar_one_or_none()


async def get_empresa_by_slug(db: AsyncSession, slug: str) -> Empresa | None:
    result = await db.execute(select(Empresa).where(Empresa.slug == slug))
    return result.scalar_one_or_none()


async def create_empresa(db: AsyncSession, data: dict) -> Empresa:
    empresa = Empresa(
        nombre=data["nombre"],
        slug=data["slug"],
        id_plan=data.get("id_plan", 1),
        timezone=data.get("timezone", "America/Argentina/Buenos_Aires"),
        activa=data.get("activa", True),
        permite_followup=False,
        servicios={"bot": True, "landing": False},
        notificaciones={},
    )
    db.add(empresa)
    await db.flush()
    await db.refresh(empresa)
    return empresa


async def update_empresa(db: AsyncSession, empresa: Empresa, data: dict) -> Empresa:
    for field, value in data.items():
        if value is not None:
            setattr(empresa, field, value)
    await db.flush()
    await db.refresh(empresa)
    return empresa


async def toggle_activa(db: AsyncSession, empresa: Empresa, activa: bool) -> Empresa:
    empresa.activa = activa
    await db.flush()
    await db.refresh(empresa)
    return empresa