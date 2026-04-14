"""
admin_usuarios.py — CRUD de usuarios para el panel superadmin.

Rutas:
  GET    /admin/usuarios                      — listado con filtros
  GET    /admin/usuarios/{id}                 — detalle
  POST   /admin/usuarios                      — alta
  PUT    /admin/usuarios/{id}                 — edición
  PATCH  /admin/usuarios/{id}/activo          — toggle activo
  POST   /admin/usuarios/{id}/reset-password  — cambio de contraseña
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.api_models import (
    UsuarioAdminResponse,
    UsuarioCreateRequest,
    UsuarioListResponse,
    UsuarioResetPasswordRequest,
    UsuarioUpdateRequest,
)
from app.models.db_models import UsuarioAdmin
from app.repositories import empresas_repository as emp_repo
from app.repositories import usuarios_repository as repo

router = APIRouter()


def _require_superadmin(current_user: UsuarioAdmin) -> None:
    if not current_user.es_superadmin:
        raise HTTPException(status_code=403, detail="Acceso restringido a superadmin.")


def _to_response(u: UsuarioAdmin) -> UsuarioAdminResponse:
    empresa_nombre: str | None = None
    if not u.es_superadmin and u.empresa:
        empresa_nombre = u.empresa.nombre
    return UsuarioAdminResponse(
        id_usuario=u.id_usuario,
        nombre=u.nombre,
        email=u.email,
        es_superadmin=u.es_superadmin,
        activo=u.activo,
        id_empresa=u.id_empresa if not u.es_superadmin else None,
        empresa_nombre=empresa_nombre,
        created_at=u.created_at.isoformat() if u.created_at else None,
    )


@router.get("", response_model=UsuarioListResponse)
async def list_usuarios(
    activo: bool | None = Query(None),
    es_superadmin: bool | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)
    usuarios, total = await repo.list_usuarios(
        db, activo=activo, es_superadmin=es_superadmin, offset=offset, limit=limit
    )
    return UsuarioListResponse(usuarios=[_to_response(u) for u in usuarios], total=total)


@router.get("/{id_usuario}", response_model=UsuarioAdminResponse)
async def get_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)
    usuario = await repo.get_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return _to_response(usuario)


@router.post("", response_model=UsuarioAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    body: UsuarioCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)

    if await repo.get_usuario_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="El email ya está en uso.")

    if body.es_superadmin:
        # Superadmin usa la empresa plataforma del current_user
        id_empresa = current_user.id_empresa
    else:
        if not body.id_empresa:
            raise HTTPException(status_code=422, detail="La empresa es obligatoria para usuarios cliente.")
        empresa = await emp_repo.get_empresa(db, body.id_empresa)
        if not empresa or not empresa.activa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva.")
        id_empresa = body.id_empresa

    usuario = await repo.create_usuario(db, {
        "nombre": body.nombre,
        "email": body.email,
        "password": body.password,
        "es_superadmin": body.es_superadmin,
        "id_empresa": id_empresa,
    })
    await db.commit()
    # Recargar con relación empresa
    usuario = await repo.get_usuario(db, usuario.id_usuario)
    return _to_response(usuario)


@router.put("/{id_usuario}", response_model=UsuarioAdminResponse)
async def update_usuario(
    id_usuario: int,
    body: UsuarioUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)

    usuario = await repo.get_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    is_own = (id_usuario == current_user.id_usuario)
    updates: dict = {}

    if body.nombre is not None:
        if len(body.nombre.strip()) < 2:
            raise HTTPException(status_code=422, detail="El nombre debe tener al menos 2 caracteres.")
        updates["nombre"] = body.nombre.strip()

    if body.email is not None and body.email != usuario.email:
        if await repo.get_usuario_by_email(db, body.email):
            raise HTTPException(status_code=409, detail="El email ya está en uso.")
        updates["email"] = body.email

    # activo, rol y empresa solo editables si no es el propio usuario
    if not is_own:
        if body.activo is not None:
            updates["activo"] = body.activo

        if body.es_superadmin is not None:
            updates["es_superadmin"] = body.es_superadmin
            if body.es_superadmin:
                # Pasa a superadmin: asignar empresa plataforma
                updates["id_empresa"] = current_user.id_empresa
            else:
                # Pasa a cliente: requiere empresa
                if not body.id_empresa:
                    raise HTTPException(status_code=422, detail="La empresa es obligatoria para usuarios cliente.")
                empresa = await emp_repo.get_empresa(db, body.id_empresa)
                if not empresa or not empresa.activa:
                    raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva.")
                updates["id_empresa"] = body.id_empresa
        elif body.id_empresa is not None and not usuario.es_superadmin:
            # Cambio de empresa sin cambio de rol (solo clientes)
            empresa = await emp_repo.get_empresa(db, body.id_empresa)
            if not empresa or not empresa.activa:
                raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva.")
            updates["id_empresa"] = body.id_empresa

    if updates:
        await repo.update_usuario(db, usuario, updates)
        await db.commit()

    usuario = await repo.get_usuario(db, id_usuario)
    return _to_response(usuario)


@router.patch("/{id_usuario}/activo", response_model=UsuarioAdminResponse)
async def toggle_activo(
    id_usuario: int,
    activo: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)
    if id_usuario == current_user.id_usuario:
        raise HTTPException(status_code=400, detail="No podés desactivarte a vos mismo.")
    usuario = await repo.get_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    usuario = await repo.toggle_activo(db, usuario, activo)
    await db.commit()
    return _to_response(usuario)


@router.post("/{id_usuario}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    id_usuario: int,
    body: UsuarioResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    _require_superadmin(current_user)
    usuario = await repo.get_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    await repo.reset_password(db, usuario, body.nueva_password)
    await db.commit()