"""
admin_empresas.py — CRUD de empresas para el panel superadmin.

Rutas:
  GET    /admin/empresas          — listado con filtro activa
  GET    /admin/empresas/{id}     — detalle de una empresa
  POST   /admin/empresas          — alta de empresa
  PUT    /admin/empresas/{id}     — edición completa
  PATCH  /admin/empresas/{id}/activa — toggle activa
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.api_models import (
    CatalogoRepoResponse,
    CatalogoRepoUpdateRequest,
    EmpresaAdminResponse,
    EmpresaCreateRequest,
    EmpresaListResponse,
    EmpresaNotificacionesSchema,
    EmpresaServiciosSchema,
    EmpresaUpdateRequest,
)
from app.models.db_models import EmpresaRubro, EmpresaRuboCatalogo, UsuarioAdmin
from app.repositories import empresas_repository as repo

_ID_RUBRO_INMOBILIARIA = 1

router = APIRouter()


def _to_response(e) -> EmpresaAdminResponse:
    srv = e.servicios or {}
    notif = e.notificaciones or {}
    tg = notif.get("telegram", {})
    em = notif.get("email", {})
    return EmpresaAdminResponse(
        id_empresa=e.id_empresa,
        nombre=e.nombre,
        slug=e.slug,
        id_plan=e.id_plan,
        activa=e.activa,
        permite_followup=e.permite_followup,
        timezone=e.timezone,
        servicios=EmpresaServiciosSchema(
            bot=srv.get("bot", True),
            landing=srv.get("landing", False),
            catalogo_repo=srv.get("catalogo_repo", False),
            panel_cliente=srv.get("panel_cliente", False),
        ),
        notificaciones=EmpresaNotificacionesSchema.model_validate({
            "telegram": {"enabled": tg.get("enabled", False), "chat_id": str(tg.get("chat_id", ""))},
            "email": {"enabled": em.get("enabled", False), "to": em.get("to", "")},
        }),
        created_at=e.created_at.isoformat() if e.created_at else None,
    )


@router.get("", response_model=EmpresaListResponse)
async def list_empresas(
    activa: bool | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresas, total = await repo.list_empresas(db, activa=activa, offset=offset, limit=limit)
    return EmpresaListResponse(
        empresas=[_to_response(e) for e in empresas],
        total=total,
    )


@router.get("/{id_empresa}", response_model=EmpresaAdminResponse)
async def get_empresa(
    id_empresa: int,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    return _to_response(empresa)


@router.post("", response_model=EmpresaAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_empresa(
    body: EmpresaCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    existing = await repo.get_empresa_by_slug(db, body.slug)
    if existing:
        raise HTTPException(status_code=409, detail="El slug ya está en uso.")

    empresa = await repo.create_empresa(db, body.model_dump())
    await db.commit()
    return _to_response(empresa)


@router.put("/{id_empresa}", response_model=EmpresaAdminResponse)
async def update_empresa(
    id_empresa: int,
    body: EmpresaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    updates: dict = {}
    if body.nombre is not None:
        updates["nombre"] = body.nombre
    if body.id_plan is not None:
        updates["id_plan"] = body.id_plan
    if body.activa is not None:
        updates["activa"] = body.activa
    if body.permite_followup is not None:
        updates["permite_followup"] = body.permite_followup
    if body.timezone is not None:
        updates["timezone"] = body.timezone
    if body.servicios is not None:
        updates["servicios"] = body.servicios.model_dump()
    if body.notificaciones is not None:
        notif = body.notificaciones
        updates["notificaciones"] = {
            "telegram": {"enabled": notif.telegram.enabled, "chat_id": notif.telegram.chat_id},
            "email": {"enabled": notif.email.enabled, "to": notif.email.to},
        }

    empresa = await repo.update_empresa(db, empresa, updates)
    await db.commit()
    return _to_response(empresa)


@router.patch("/{id_empresa}/activa", response_model=EmpresaAdminResponse)
async def toggle_activa(
    id_empresa: int,
    activa: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    empresa = await repo.toggle_activa(db, empresa, activa)
    await db.commit()
    return _to_response(empresa)


@router.delete("/{id_empresa}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_empresa(
    id_empresa: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    if id_empresa == current_user.id_empresa:
        raise HTTPException(status_code=400, detail="No podés eliminar tu propia empresa.")
    usuarios = await repo.count_usuarios(db, id_empresa)
    if usuarios > 0:
        raise HTTPException(
            status_code=409,
            detail=f"La empresa tiene {usuarios} usuario(s) asociado(s). Eliminá los usuarios primero.",
        )
    await repo.delete_empresa(db, empresa)
    await db.commit()


# ─── Catalogo repo config ─────────────────────────────────────────────────────

def _catalogo_to_response(c: EmpresaRuboCatalogo) -> CatalogoRepoResponse:
    return CatalogoRepoResponse(
        id_empresa=c.id_empresa,
        id_rubro=c.id_rubro,
        activo=c.activo,
        catalog_source=c.catalog_source,
        export_format=c.export_format,
        github_repo=c.github_repo,
        github_branch=c.github_branch,
        github_path=c.github_path,
        github_raw_url=c.github_raw_url,
    )


@router.get("/{id_empresa}/catalogo", response_model=CatalogoRepoResponse | None)
async def get_catalogo(
    id_empresa: int,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    result = await db.execute(
        select(EmpresaRuboCatalogo).where(
            EmpresaRuboCatalogo.id_empresa == id_empresa,
            EmpresaRuboCatalogo.id_rubro == _ID_RUBRO_INMOBILIARIA,
        )
    )
    catalogo = result.scalar_one_or_none()
    return _catalogo_to_response(catalogo) if catalogo else None


@router.put("/{id_empresa}/catalogo", response_model=CatalogoRepoResponse)
async def upsert_catalogo(
    id_empresa: int,
    body: CatalogoRepoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(get_current_admin),
):
    empresa = await repo.get_empresa(db, id_empresa)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    # Garantizar que empresa_rubros tenga el registro (FK requerida por empresa_rubro_catalogos)
    empresa_rubro = (await db.execute(
        select(EmpresaRubro).where(
            EmpresaRubro.id_empresa == id_empresa,
            EmpresaRubro.id_rubro == _ID_RUBRO_INMOBILIARIA,
        )
    )).scalar_one_or_none()
    if empresa_rubro is None:
        db.add(EmpresaRubro(
            id_empresa=id_empresa,
            id_rubro=_ID_RUBRO_INMOBILIARIA,
            activo=True,
            es_default=True,
        ))
        await db.flush()

    result = await db.execute(
        select(EmpresaRuboCatalogo).where(
            EmpresaRuboCatalogo.id_empresa == id_empresa,
            EmpresaRuboCatalogo.id_rubro == _ID_RUBRO_INMOBILIARIA,
        )
    )
    catalogo = result.scalar_one_or_none()

    if catalogo is None:
        catalogo = EmpresaRuboCatalogo(
            id_empresa=id_empresa,
            id_rubro=_ID_RUBRO_INMOBILIARIA,
            activo=True,
            catalog_source=body.catalog_source or "github",
            export_format=body.export_format or "inmo_v1",
        )
        db.add(catalogo)

    if body.github_repo is not None:
        catalogo.github_repo = body.github_repo
    if body.github_branch is not None:
        catalogo.github_branch = body.github_branch
    if body.github_path is not None:
        catalogo.github_path = body.github_path
    if body.github_raw_url is not None:
        catalogo.github_raw_url = body.github_raw_url
    if body.catalog_source is not None:
        catalogo.catalog_source = body.catalog_source
    if body.export_format is not None:
        catalogo.export_format = body.export_format

    await db.flush()
    await db.refresh(catalogo)
    await db.commit()
    return _catalogo_to_response(catalogo)