"""
Endpoints de leads para el panel administrativo.
Protegidos con JWT (get_current_admin).
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.api_models import (
    LeadDetailResponse,
    LeadListResponse,
    LeadResponse,
    LeadUpdateRequest,
    PropiedadDetalle,
)
from app.models.db_models import UsuarioAdmin
from app.services.leads_service import LeadsService

router = APIRouter()


async def _enriquecer_propiedades(
    db: AsyncSession,
    metadata: dict,
) -> list[PropiedadDetalle]:
    """Lookup en items por los IDs guardados en propiedades_interes."""
    props_meta = metadata.get("propiedades_interes", [])
    if not props_meta:
        return []

    # Extraer UUIDs válidos
    ids: list[uuid.UUID] = []
    titulos_fallback: dict[str, str] = {}
    for p in props_meta:
        raw_id = p.get("id", "")
        try:
            ids.append(uuid.UUID(raw_id))
            titulos_fallback[raw_id] = p.get("titulo", "")
        except (ValueError, AttributeError):
            pass

    if not ids:
        return [
            PropiedadDetalle(id=p.get("id", ""), titulo=p.get("titulo", ""))
            for p in props_meta
        ]

    result = await db.execute(
        text("""
            SELECT id_item::text, titulo, tipo, categoria, atributos
            FROM items
            WHERE id_item = ANY(:ids)
        """),
        {"ids": ids},
    )
    rows = result.mappings().all()

    items_by_id = {r["id_item"]: r for r in rows}

    detalle: list[PropiedadDetalle] = []
    for p in props_meta:
        raw_id = p.get("id", "")
        row = items_by_id.get(raw_id)
        if row:
            attr = row["atributos"] or {}
            detalle.append(PropiedadDetalle(
                id=raw_id,
                titulo=row["titulo"],
                tipo=row["tipo"],
                categoria=row["categoria"],
                direccion=attr.get("calle"),
                ciudad=attr.get("ciudad"),
                barrio=attr.get("barrio"),
                dormitorios=attr.get("dormitorios"),
                banios=attr.get("banios"),
                superficie_cubierta=attr.get("superficie_cubierta"),
            ))
        else:
            detalle.append(PropiedadDetalle(
                id=raw_id,
                titulo=titulos_fallback.get(raw_id, "—"),
            ))

    return detalle


@router.get("", response_model=LeadListResponse)
async def list_leads(
    estado: str | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> LeadListResponse:
    service = LeadsService(db)
    return await service.list_leads(
        id_empresa=current_user.id_empresa,
        estado=estado,
        page=page,
        page_size=page_size,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/{id_lead}", response_model=LeadDetailResponse)
async def get_lead(
    id_lead: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> LeadDetailResponse:
    service = LeadsService(db)
    lead = await service.get_lead(id_lead, current_user.id_empresa)
    propiedades = await _enriquecer_propiedades(db, lead.metadata)
    return LeadDetailResponse(**lead.model_dump(), propiedades_detalle=propiedades)


@router.patch("/{id_lead}", response_model=LeadResponse)
async def update_lead(
    id_lead: int,
    body: LeadUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> LeadResponse:
    service = LeadsService(db)
    await service.get_lead(id_lead, current_user.id_empresa)
    return await service.update_lead(id_lead, body)