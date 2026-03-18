from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.api_models import LeadCreateRequest, LeadListResponse, LeadResponse, LeadUpdateRequest
from app.services.leads_service import LeadsService

router = APIRouter()


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    request: LeadCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> LeadResponse:
    """Crea un lead manualmente (uso administrativo o externo)."""
    service = LeadsService(db)
    return await service.create_lead(request)


@router.get("", response_model=LeadListResponse)
async def list_leads(
    id_empresa: int = Query(...),
    estado: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> LeadListResponse:
    """Lista de leads de una empresa."""
    service = LeadsService(db)
    return await service.list_leads(id_empresa, estado, page, page_size)


@router.patch("/{id_lead}", response_model=LeadResponse)
async def update_lead(
    id_lead: int,
    request: LeadUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> LeadResponse:
    """Actualiza un lead existente."""
    service = LeadsService(db)
    return await service.update_lead(id_lead, request)
