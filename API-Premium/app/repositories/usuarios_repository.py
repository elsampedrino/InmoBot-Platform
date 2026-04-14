"""
usuarios_repository.py — Operaciones CRUD sobre usuarios_admin.
Usado exclusivamente por admin_usuarios.py (panel superadmin).
"""
import bcrypt as _bcrypt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db_models import UsuarioAdmin


async def list_usuarios(
    db: AsyncSession,
    activo: bool | None = None,
    es_superadmin: bool | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[UsuarioAdmin], int]:
    q = select(UsuarioAdmin).options(selectinload(UsuarioAdmin.empresa))
    if activo is not None:
        q = q.where(UsuarioAdmin.activo == activo)
    if es_superadmin is not None:
        q = q.where(UsuarioAdmin.es_superadmin == es_superadmin)
    q = q.order_by(UsuarioAdmin.nombre.asc())

    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), total


async def get_usuario(db: AsyncSession, id_usuario: int) -> UsuarioAdmin | None:
    result = await db.execute(
        select(UsuarioAdmin)
        .where(UsuarioAdmin.id_usuario == id_usuario)
        .options(selectinload(UsuarioAdmin.empresa))
    )
    return result.scalar_one_or_none()


async def get_usuario_by_email(db: AsyncSession, email: str) -> UsuarioAdmin | None:
    result = await db.execute(
        select(UsuarioAdmin).where(UsuarioAdmin.email == email)
    )
    return result.scalar_one_or_none()


def _hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


async def create_usuario(db: AsyncSession, data: dict) -> UsuarioAdmin:
    usuario = UsuarioAdmin(
        nombre=data.get("nombre"),
        email=data["email"],
        password_hash=_hash_password(data["password"]),
        es_superadmin=data.get("es_superadmin", False),
        id_empresa=data["id_empresa"],
        activo=True,
    )
    db.add(usuario)
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def update_usuario(db: AsyncSession, usuario: UsuarioAdmin, data: dict) -> UsuarioAdmin:
    for field, value in data.items():
        setattr(usuario, field, value)
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def toggle_activo(db: AsyncSession, usuario: UsuarioAdmin, activo: bool) -> UsuarioAdmin:
    usuario.activo = activo
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def reset_password(db: AsyncSession, usuario: UsuarioAdmin, nueva_password: str) -> UsuarioAdmin:
    usuario.password_hash = _hash_password(nueva_password)
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def count_superadmins(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).where(UsuarioAdmin.es_superadmin == True)  # noqa: E712
    )
    return result.scalar_one()


async def delete_usuario(db: AsyncSession, usuario: UsuarioAdmin) -> None:
    await db.delete(usuario)
    await db.flush()