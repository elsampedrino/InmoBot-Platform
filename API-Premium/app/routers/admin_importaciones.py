"""
admin_importaciones.py — Módulo de importación/sincronización de catálogo.

Rutas:
  POST /admin/importaciones/preview          — diff entre JSON y DB actual
  POST /admin/importaciones/aplicar-db       — aplica el diff a la DB
  POST /admin/importaciones/publicar-github  — exporta items activos a GitHub
  GET  /admin/importaciones/logs             — historial de importaciones por empresa
"""
import json
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.config import settings
from app.core.database import get_db
from app.models.api_models import (
    ImportacionAplicarRequest,
    ImportacionAplicarResponse,
    ImportacionItemModificado,
    ImportacionLogListResponse,
    ImportacionLogResponse,
    ImportacionPreviewItem,
    ImportacionPreviewRequest,
    ImportacionPreviewResponse,
    ImportacionPublicarRequest,
    ImportacionPublicarResponse,
)
from app.models.db_models import UsuarioAdmin
from app.repositories import empresas_repository as emp_repo
from app.repositories import importaciones_repository as repo
from app.repositories.items_repository import ItemsRepository
from app.routers.admin_items import _item_to_landing_format

router = APIRouter()

_ID_RUBRO_INMOBILIARIA = 1


def _require_superadmin(current_user: UsuarioAdmin) -> None:
    if not current_user.es_superadmin:
        raise HTTPException(status_code=403, detail="Acceso restringido a superadmin.")


async def _get_empresa_or_404(db: AsyncSession, id_empresa: int):
    empresa = await emp_repo.get_empresa(db, id_empresa)
    if not empresa or not empresa.activa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva.")
    return empresa


def _extract_propiedades(catalogo: dict) -> list[dict]:
    """Extrae la lista de propiedades del JSON, sea cual sea la clave raíz."""
    if "propiedades" in catalogo:
        return catalogo["propiedades"]
    if "items" in catalogo:
        return catalogo["items"]
    # Si es una lista directamente
    if isinstance(catalogo, list):
        return catalogo
    raise HTTPException(
        status_code=422,
        detail="El JSON no contiene la clave 'propiedades'.",
    )


# ─── Preview ──────────────────────────────────────────────────────────────────

@router.post("/preview", response_model=ImportacionPreviewResponse)
async def preview_importacion(
    body: ImportacionPreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ImportacionPreviewResponse:
    _require_superadmin(current_user)
    await _get_empresa_or_404(db, body.id_empresa)

    propiedades = _extract_propiedades(body.catalogo)
    db_items = await repo.get_items_for_diff(db, body.id_empresa)
    diff = repo.compute_diff(db_items, propiedades)

    return ImportacionPreviewResponse(
        id_empresa=body.id_empresa,
        total_json=len(propiedades),
        total_db=len(db_items),
        nuevos=[
            ImportacionPreviewItem(
                external_id=i["external_id"],
                titulo=i["titulo"],
                tipo=i["tipo"],
                categoria=i["categoria"],
            )
            for i in diff["nuevos"]
        ],
        modificados=[
            ImportacionItemModificado(
                external_id=i["external_id"],
                titulo=i["titulo"],
                tipo=i["tipo"],
                categoria=i["categoria"],
                cambios=i["cambios"],
            )
            for i in diff["modificados"]
        ],
        sin_cambios=diff["sin_cambios"],
        a_desactivar=[
            ImportacionPreviewItem(
                external_id=i["external_id"],
                titulo=i["titulo"],
                tipo=i["tipo"],
                categoria=i["categoria"],
            )
            for i in diff["a_desactivar"]
        ],
    )


# ─── Aplicar DB ───────────────────────────────────────────────────────────────

@router.post("/aplicar-db", response_model=ImportacionAplicarResponse)
async def aplicar_importacion(
    body: ImportacionAplicarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ImportacionAplicarResponse:
    _require_superadmin(current_user)
    await _get_empresa_or_404(db, body.id_empresa)

    propiedades = _extract_propiedades(body.catalogo)
    db_items = await repo.get_items_for_diff(db, body.id_empresa)
    diff = repo.compute_diff(db_items, propiedades)

    insertados, actualizados, desactivados = await repo.apply_diff(
        db,
        id_empresa=body.id_empresa,
        id_rubro=_ID_RUBRO_INMOBILIARIA,
        nuevos=diff["nuevos"],
        modificados=diff["modificados"],
        a_desactivar=diff["a_desactivar"],
    )

    log = await repo.create_log(db, {
        "id_empresa": body.id_empresa,
        "accion": "aplicar_db",
        "resultado": "ok",
        "detalle": {
            "insertados": insertados,
            "actualizados": actualizados,
            "desactivados": desactivados,
            "sin_cambios": diff["sin_cambios"],
            "total_json": len(propiedades),
        },
        "id_usuario": current_user.id_usuario,
        "nombre_usuario": current_user.nombre or current_user.email,
    })

    await db.commit()

    return ImportacionAplicarResponse(
        ok=True,
        insertados=insertados,
        actualizados=actualizados,
        desactivados=desactivados,
        id_log=log.id,
        message=(
            f"Catálogo actualizado: {insertados} nuevos, "
            f"{actualizados} modificados, {desactivados} desactivados."
        ),
    )


# ─── Publicar GitHub ──────────────────────────────────────────────────────────

@router.post("/publicar-github", response_model=ImportacionPublicarResponse)
async def publicar_github(
    body: ImportacionPublicarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ImportacionPublicarResponse:
    _require_superadmin(current_user)
    empresa = await _get_empresa_or_404(db, body.id_empresa)

    servicios: dict = empresa.servicios or {}
    if not servicios.get("landing"):
        raise HTTPException(
            status_code=403,
            detail="Esta empresa no tiene habilitado el servicio de landing.",
        )

    if not settings.GITHUB_TOKEN:
        raise HTTPException(status_code=503, detail="GITHUB_TOKEN no configurado.")

    items_repo = ItemsRepository(db)
    rows = await items_repo.admin_list_activos_export(body.id_empresa)
    propiedades = [_item_to_landing_format(r) for r in rows]

    payload: dict[str, Any] = {
        "metadata": {
            "ultima_actualizacion": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total": len(propiedades),
            "fuente": "Panel Admin InmoBot — Importaciones",
        },
        "propiedades": propiedades,
    }
    content = json.dumps(payload, indent=2, ensure_ascii=False)

    commit_sha = await _github_push(content, len(propiedades))

    log = await repo.create_log(db, {
        "id_empresa": body.id_empresa,
        "accion": "publicar_github",
        "resultado": "ok",
        "detalle": {
            "total_propiedades": len(propiedades),
            "commit_sha": commit_sha,
        },
        "id_usuario": current_user.id_usuario,
        "nombre_usuario": current_user.nombre or current_user.email,
    })

    await db.commit()

    return ImportacionPublicarResponse(
        ok=True,
        total=len(propiedades),
        commit_sha=commit_sha,
        id_log=log.id,
        message=f"Publicadas {len(propiedades)} propiedades en GitHub (commit {commit_sha}).",
    )


# ─── Logs ─────────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=ImportacionLogListResponse)
async def list_logs(
    id_empresa: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ImportacionLogListResponse:
    _require_superadmin(current_user)
    if id_empresa is not None:
        await _get_empresa_or_404(db, id_empresa)

    logs, total = await repo.list_logs(db, id_empresa=id_empresa, limit=limit)

    return ImportacionLogListResponse(
        logs=[
            ImportacionLogResponse(
                id=log.id,
                id_empresa=log.id_empresa,
                empresa_nombre=log.empresa.nombre if log.empresa else None,
                accion=log.accion,
                resultado=log.resultado,
                detalle=log.detalle or {},
                nombre_usuario=log.nombre_usuario,
                created_at=log.created_at.isoformat() if log.created_at else None,
            )
            for log in logs
        ],
        total=total,
    )


# ─── GitHub helper ────────────────────────────────────────────────────────────

async def _github_push(content: str, total: int) -> str | None:
    import base64
    token = settings.GITHUB_TOKEN
    owner = settings.GITHUB_REPO_OWNER
    repo_name = settings.GITHUB_REPO_NAME
    path = settings.GITHUB_FILE_PATH
    branch = settings.GITHUB_BRANCH

    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=headers, params={"ref": branch})
        sha = r.json().get("sha") if r.status_code == 200 else None

        content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        body: dict[str, Any] = {
            "message": (
                f"Actualizar catálogo: {total} propiedades "
                f"— {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
            ),
            "content": content_b64,
            "branch": branch,
        }
        if sha:
            body["sha"] = sha

        r2 = await client.put(url, headers=headers, json=body)
        if r2.status_code in (200, 201):
            return r2.json()["commit"]["sha"][:7]
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error {r2.status_code}: {r2.text[:200]}",
        )