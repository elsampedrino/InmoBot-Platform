"""
ItemsRepository — acceso a la tabla items (catálogo).

Responsabilidades:
- Búsquedas filtradas con WHERE dinámico
- Lookup por id_item
- Listados administrativos paginados
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Item


class ItemsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(
        self,
        id_empresa: int,
        id_rubro: int,
        where_clauses: list,
        params: dict,
        limit: int = 5,
    ) -> list[Item]:
        """Ejecuta la búsqueda con cláusulas WHERE dinámicas."""
        raise NotImplementedError

    async def get_by_id(self, id_item: uuid.UUID) -> Item | None:
        raise NotImplementedError

    async def list_by_empresa(
        self,
        id_empresa: int,
        activo: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[Item], int]:
        """Devuelve (items, total)."""
        raise NotImplementedError
