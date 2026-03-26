"""
Autenticación del panel admin.

- create_access_token: genera JWT para un usuario admin
- get_current_admin: dependency FastAPI que valida el Bearer token
  y devuelve el UsuarioAdmin autenticado con su empresa cargada
"""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.db_models import Empresa, UsuarioAdmin

_bearer = HTTPBearer()


def create_access_token(id_usuario: int, empresa_slug: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ADMIN_JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(id_usuario), "slug": empresa_slug, "exp": expire},
        settings.ADMIN_JWT_SECRET,
        algorithm="HS256",
    )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> UsuarioAdmin:
    """
    Valida el Bearer token y devuelve el UsuarioAdmin con empresa cargada.
    Lanza 401 si el token es inválido, expirado o el usuario está inactivo.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.ADMIN_JWT_SECRET,
            algorithms=["HS256"],
        )
        id_usuario = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(UsuarioAdmin)
        .where(UsuarioAdmin.id_usuario == id_usuario, UsuarioAdmin.activo == True)  # noqa: E712
        .options(selectinload(UsuarioAdmin.empresa))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user