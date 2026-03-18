"""
CatalogService — operaciones no-conversacionales sobre el catálogo.

Responsabilidades:
- Listar items con paginación (uso administrativo)
- Obtener item por ID
- Importar/exportar catálogo

No debe:
- Asumir comportamiento conversacional
- Reemplazar al SearchEngine para búsquedas guiadas
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_models import ItemListResponse, ItemResponse


class CatalogService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_items(
        self,
        empresa_slug: str,
        activo: bool,
        page: int,
        page_size: int,
    ) -> ItemListResponse:
        """Lista paginada de items del catálogo."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_item(self, id_item: str) -> ItemResponse:
        """Detalle de un item por UUID. Raises 404 si no existe."""
        # TODO Fase 6
        raise NotImplementedError
