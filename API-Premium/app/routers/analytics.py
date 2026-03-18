from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.api_models import AnalyticsSummaryResponse, ChatLogResponse, ConversionLogResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    id_empresa: int = Query(...),
    dias: int = Query(30, ge=1, le=365, description="Período en días"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> AnalyticsSummaryResponse:
    """Resumen de métricas del período."""
    service = AnalyticsService(db)
    return await service.get_summary(id_empresa, dias)


@router.get("/chats", response_model=list[ChatLogResponse])
async def list_chat_logs(
    id_empresa: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> list[ChatLogResponse]:
    """Lista de logs de chat del período."""
    service = AnalyticsService(db)
    return await service.get_chat_logs(id_empresa, page, page_size)


@router.get("/conversiones", response_model=list[ConversionLogResponse])
async def list_conversion_logs(
    id_empresa: int = Query(...),
    evento: str | None = Query(None, description="Filtrar por tipo de evento"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> list[ConversionLogResponse]:
    """Lista de eventos de conversión."""
    service = AnalyticsService(db)
    return await service.get_conversion_logs(id_empresa, evento, page, page_size)
