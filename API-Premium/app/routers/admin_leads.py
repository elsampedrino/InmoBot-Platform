"""
Endpoints de leads para el panel administrativo.
Protegidos con JWT (get_current_admin).
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.api_models import LeadListResponse, LeadResponse, LeadUpdateRequest
from app.models.db_models import UsuarioAdmin
from app.services.leads_service import LeadsService

router = APIRouter()


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


@router.get("/{id_lead}", response_model=LeadResponse)
async def get_lead(
    id_lead: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> LeadResponse:
    service = LeadsService(db)
    return await service.get_lead(id_lead, current_user.id_empresa)


@router.patch("/{id_lead}", response_model=LeadResponse)
async def update_lead(
    id_lead: int,
    body: LeadUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
) -> LeadResponse:
    service = LeadsService(db)
    # Verificar pertenencia antes de actualizar
    await service.get_lead(id_lead, current_user.id_empresa)
    return await service.update_lead(id_lead, body)