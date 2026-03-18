from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.api_models import ItemListResponse, ItemResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/items", response_model=ItemListResponse)
async def list_items(
    empresa_slug: str = Query(..., description="Slug de la empresa"),
    activo: bool = Query(True, description="Filtrar por activos"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> ItemListResponse:
    """Lista de items del catálogo (uso administrativo)."""
    service = CatalogService(db)
    return await service.list_items(empresa_slug, activo, page, page_size)


@router.get("/items/{id_item}", response_model=ItemResponse)
async def get_item(
    id_item: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> ItemResponse:
    """Detalle de un item por ID."""
    service = CatalogService(db)
    return await service.get_item(id_item)
