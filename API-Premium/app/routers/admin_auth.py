"""
Endpoints de autenticación del panel admin.

POST /admin/auth/login  — recibe email + password, devuelve JWT + contexto
GET  /admin/auth/me     — devuelve usuario y empresa del token actual
"""
import bcrypt as _bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.admin_auth import create_access_token, get_current_admin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class EmpresaInfo(BaseModel):
    id_empresa: int
    nombre: str
    slug: str | None
    servicios: dict


class UsuarioInfo(BaseModel):
    id_usuario: int
    nombre: str | None
    email: str
    es_superadmin: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioInfo
    empresa: EmpresaInfo


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioAdmin)
        .where(UsuarioAdmin.email == body.email, UsuarioAdmin.activo == True)  # noqa: E712
        .options(selectinload(UsuarioAdmin.empresa))
    )
    user = result.scalar_one_or_none()

    if not user or not _bcrypt.checkpw(body.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    empresa = user.empresa
    token = create_access_token(user.id_usuario, empresa.slug or "")

    return LoginResponse(
        access_token=token,
        usuario=UsuarioInfo(
            id_usuario=user.id_usuario,
            nombre=user.nombre,
            email=user.email,
            es_superadmin=user.es_superadmin,
        ),
        empresa=EmpresaInfo(
            id_empresa=empresa.id_empresa,
            nombre=empresa.nombre,
            slug=empresa.slug,
            servicios=empresa.servicios or {"bot": True},
        ),
    )


@router.get("/me", response_model=LoginResponse)
async def me(current_user: UsuarioAdmin = Depends(get_current_admin)):
    empresa = current_user.empresa
    token = create_access_token(current_user.id_usuario, empresa.slug or "")

    return LoginResponse(
        access_token=token,
        usuario=UsuarioInfo(
            id_usuario=current_user.id_usuario,
            nombre=current_user.nombre,
            email=current_user.email,
            es_superadmin=current_user.es_superadmin,
        ),
        empresa=EmpresaInfo(
            id_empresa=empresa.id_empresa,
            nombre=empresa.nombre,
            slug=empresa.slug,
            servicios=empresa.servicios or {"bot": True},
        ),
    )