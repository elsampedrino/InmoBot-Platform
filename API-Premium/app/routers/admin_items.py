"""
Endpoints de items (propiedades) para el panel administrativo.
Protegidos con JWT (get_current_admin).
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.admin_auth import get_current_admin
from app.core.config import settings
from app.core.database import get_db
from app.models.api_models import (
    CloudinarySignResponse,
    ExportLandingResponse,
    ItemAdminListResponse,
    ItemAdminResponse,
    ItemCreateRequest,
    ItemUpdateRequest,
)
from app.models.db_models import EmpresaRuboCatalogo, UsuarioAdmin
from app.repositories.items_repository import ItemsRepository

router = APIRouter()

# Rubro inmobiliaria
_ID_RUBRO_INMOBILIARIA = 1


def _row_to_response(row: dict) -> ItemAdminResponse:
    created = row.get("created_at")
    if created is not None and hasattr(created, "isoformat"):
        created = created.isoformat()
    return ItemAdminResponse(
        id_item=row["id_item"],
        external_id=row["external_id"],
        tipo=row["tipo"],
        categoria=row.get("categoria"),
        titulo=row["titulo"],
        descripcion=row.get("descripcion"),
        descripcion_corta=row.get("descripcion_corta"),
        precio=row.get("precio"),
        moneda=row.get("moneda"),
        activo=row["activo"],
        destacado=row["destacado"],
        atributos=row.get("atributos") or {},
        media=row.get("media") or {},
        created_at=created,
    )


# ── List ───────────────────────────────────────────────────────────────────────

@router.get("", response_model=ItemAdminListResponse)
async def list_items(
    activo: bool | None = Query(None),
    tipo: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminListResponse:
    repo = ItemsRepository(db)
    offset = (page - 1) * page_size
    rows, total = await repo.admin_list(
        id_empresa=current_user.id_empresa,
        activo=activo,
        tipo=tipo,
        offset=offset,
        limit=page_size,
    )
    return ItemAdminListResponse(
        items=[_row_to_response(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


# ── Get ────────────────────────────────────────────────────────────────────────

@router.get("/{id_item}", response_model=ItemAdminResponse)
async def get_item(
    id_item: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminResponse:
    repo = ItemsRepository(db)
    row = await repo.admin_get(current_user.id_empresa, id_item)
    if not row:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return _row_to_response(row)


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=ItemAdminResponse, status_code=201)
async def create_item(
    body: ItemCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminResponse:
    repo = ItemsRepository(db)
    data = body.model_dump()
    data["external_id"] = await repo.next_external_id(current_user.id_empresa)
    row = await repo.admin_create(
        id_empresa=current_user.id_empresa,
        id_rubro=_ID_RUBRO_INMOBILIARIA,
        data=data,
    )
    return _row_to_response(row)


# ── Update ─────────────────────────────────────────────────────────────────────

@router.put("/{id_item}", response_model=ItemAdminResponse)
async def update_item(
    id_item: str,
    body: ItemUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminResponse:
    repo = ItemsRepository(db)
    row = await repo.admin_update(
        id_empresa=current_user.id_empresa,
        id_item=id_item,
        data=body.model_dump(exclude_none=True),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return _row_to_response(row)


# ── Toggle activo ──────────────────────────────────────────────────────────────

@router.patch("/{id_item}/activo", response_model=ItemAdminResponse)
async def toggle_activo(
    id_item: str,
    activo: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminResponse:
    repo = ItemsRepository(db)
    row = await repo.admin_toggle_activo(
        id_empresa=current_user.id_empresa,
        id_item=id_item,
        activo=activo,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return _row_to_response(row)


@router.patch("/{id_item}/destacado", response_model=ItemAdminResponse)
async def toggle_destacado(
    id_item: str,
    destacado: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ItemAdminResponse:
    repo = ItemsRepository(db)
    row = await repo.admin_update(
        id_empresa=current_user.id_empresa,
        id_item=id_item,
        data={"destacado": destacado},
    )
    if not row:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return _row_to_response(row)


# ── Cloudinary sign ────────────────────────────────────────────────────────────

@router.post("/cloudinary-sign", response_model=CloudinarySignResponse)
async def cloudinary_sign(
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> CloudinarySignResponse:
    """
    Genera parámetros firmados para subir fotos directamente a Cloudinary
    desde el frontend sin exponer el API secret.
    """
    if not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(status_code=503, detail="Cloudinary no configurado")

    folder = "bbr/prop"
    transformation = "q_auto:good/f_auto"
    ts = int(time.time())
    # Parámetros ordenados alfabéticamente para la firma
    signed_params = {"folder": folder, "timestamp": ts, "transformation": transformation}
    params_str = "&".join(f"{k}={v}" for k, v in sorted(signed_params.items()))
    signature = hashlib.sha256(
        (params_str + settings.CLOUDINARY_API_SECRET).encode()
    ).hexdigest()

    return CloudinarySignResponse(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        timestamp=ts,
        signature=signature,
        folder=folder,
        transformation=transformation,
    )


# ── Export a landing (GitHub) ─────────────────────────────────────────────────

@router.post("/export-landing", response_model=ExportLandingResponse)
async def export_landing(
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> ExportLandingResponse:
    """
    Exporta las propiedades activas de la empresa al repositorio GitHub
    en formato propiedades_bbr.json para el bot y la landing.
    Solo disponible si empresa.servicios.landing = true.
    """
    # Verificar que la empresa tiene servicio de landing
    empresa = current_user.empresa
    servicios: dict = empresa.servicios or {}
    if not servicios.get("landing"):
        raise HTTPException(
            status_code=403,
            detail="Esta empresa no tiene habilitado el servicio de landing.",
        )

    if not settings.GITHUB_TOKEN:
        raise HTTPException(status_code=503, detail="GITHUB_TOKEN no configurado")

    # Leer config GitHub desde empresa_rubro_catalogos
    catalogo_cfg = (await db.execute(
        select(EmpresaRuboCatalogo).where(
            EmpresaRuboCatalogo.id_empresa == current_user.id_empresa,
            EmpresaRuboCatalogo.id_rubro == _ID_RUBRO_INMOBILIARIA,
        )
    )).scalar_one_or_none()
    if not catalogo_cfg or not catalogo_cfg.github_repo:
        raise HTTPException(
            status_code=422,
            detail="No hay configuración de GitHub para esta empresa.",
        )
    gh_owner, gh_repo_name = catalogo_cfg.github_repo.split("/", 1)

    repo = ItemsRepository(db)
    rows = await repo.admin_list_activos_export(current_user.id_empresa)

    # Convertir al formato propiedades_bbr.json
    propiedades = [_item_to_landing_format(r) for r in rows]
    payload: dict[str, Any] = {
        "metadata": {
            "ultima_actualizacion": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total": len(propiedades),
            "fuente": "Panel Admin InmoBot",
        },
        "propiedades": propiedades,
    }
    content = json.dumps(payload, indent=2, ensure_ascii=False)

    # Subir a GitHub
    commit_sha = await _github_push(
        content,
        len(propiedades),
        owner=gh_owner,
        repo_name=gh_repo_name,
        path=catalogo_cfg.github_path,
        branch=catalogo_cfg.github_branch,
    )

    return ExportLandingResponse(
        ok=True,
        total=len(propiedades),
        commit_sha=commit_sha,
        message=f"Exportadas {len(propiedades)} propiedades al repositorio.",
    )


def _item_to_landing_format(row: dict) -> dict:
    """Convierte un row de items al formato propiedades_bbr.json."""
    attr = row.get("atributos") or {}
    media = row.get("media") or {}
    fotos_urls = media.get("fotos", [])

    return {
        "id": row["external_id"],
        "tipo": (row["tipo"] or "").lower(),
        "operacion": (row.get("categoria") or "").lower(),
        "titulo": row["titulo"],
        "destacado": row["destacado"],
        "activo": row["activo"],
        "direccion": {
            "calle": attr.get("calle"),
            "barrio": attr.get("barrio"),
            "ciudad": attr.get("ciudad"),
            "lat": attr.get("lat"),
            "lng": attr.get("lng"),
        },
        "precio": {
            "valor": row.get("precio") or 0,
            "moneda": row.get("moneda") or "USD",
            "expensas": attr.get("expensas"),
        },
        "descripcion": row.get("descripcion"),
        "descripcion_corta": row.get("descripcion_corta"),
        "fotos": {
            "carpeta": row["external_id"].lower().replace("prop-", "prop-"),
            "urls": fotos_urls,
        },
        "caracteristicas": {
            "antiguedad": attr.get("antiguedad"),
            "estado_construccion": attr.get("estado_construccion"),
            "ambientes": attr.get("ambientes"),
            "dormitorios": attr.get("dormitorios"),
            "banios": attr.get("banios"),
            "superficie_total": attr.get("superficie_total"),
            "superficie_cubierta": attr.get("superficie_cubierta"),
        },
        "detalles": attr.get("detalles") or [],
    }


async def _github_push(
    content: str,
    total: int,
    *,
    owner: str,
    repo_name: str,
    path: str,
    branch: str,
) -> str | None:
    """PUT al GitHub API. Devuelve el SHA del commit o None si falla."""
    import base64
    token = settings.GITHUB_TOKEN
    repo = repo_name

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        # Obtener SHA actual del archivo
        r = await client.get(url, headers=headers, params={"ref": branch})
        sha = r.json().get("sha") if r.status_code == 200 else None

        # Codificar y subir
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