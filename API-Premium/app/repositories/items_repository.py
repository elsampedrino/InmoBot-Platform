"""
ItemsRepository — acceso a la tabla items (catálogo).

Responsabilidades:
- Búsquedas filtradas con WHERE dinámico (incluyendo JSONB)
- Lookup por id_item
- Listados administrativos paginados
"""
import json
import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Item


class ItemsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(
        self,
        id_empresa: int,
        id_rubro: int,
        where_clauses: list[str],
        params: dict,
        limit: int = 5,
    ) -> list[dict]:
        """
        Ejecuta la búsqueda con cláusulas WHERE dinámicas.
        Devuelve dicts (mappings) para incluir campos JSONB sin deserializar dos veces.
        """
        base_where = (
            "i.id_empresa = :id_empresa AND i.id_rubro = :id_rubro AND i.activo = TRUE"
        )
        extra = (" AND " + " AND ".join(where_clauses)) if where_clauses else ""
        where_sql = base_where + extra

        sql = text(f"""
            SELECT
                i.id_item::text   AS id_item,
                i.tipo,
                i.categoria,
                i.titulo,
                i.descripcion_corta,
                i.precio::float   AS precio,
                i.moneda,
                i.destacado,
                i.atributos,
                i.media,
                i.created_at
            FROM items i
            WHERE {where_sql}
            ORDER BY i.destacado DESC, i.created_at DESC
            LIMIT :limit
        """)

        all_params = {"id_empresa": id_empresa, "id_rubro": id_rubro, "limit": limit}
        all_params.update(params)

        result = await self.db.execute(sql, all_params)
        return [dict(row) for row in result.mappings()]

    async def count(
        self,
        id_empresa: int,
        id_rubro: int,
        where_clauses: list[str],
        params: dict,
    ) -> int:
        base_where = (
            "i.id_empresa = :id_empresa AND i.id_rubro = :id_rubro AND i.activo = TRUE"
        )
        extra = (" AND " + " AND ".join(where_clauses)) if where_clauses else ""
        where_sql = base_where + extra

        sql = text(f"SELECT COUNT(*) FROM items i WHERE {where_sql}")
        all_params = {"id_empresa": id_empresa, "id_rubro": id_rubro}
        all_params.update(params)

        result = await self.db.execute(sql, all_params)
        return result.scalar() or 0

    async def get_by_id(self, id_empresa: int, id_item: str) -> dict | None:
        """Devuelve el item completo por id_item (UUID string)."""
        sql = text("""
            SELECT
                i.id_item::text   AS id_item,
                i.id_empresa,
                i.id_rubro,
                i.tipo,
                i.categoria,
                i.titulo,
                i.descripcion,
                i.descripcion_corta,
                i.precio::float   AS precio,
                i.moneda,
                i.activo,
                i.destacado,
                i.atributos,
                i.media,
                i.created_at
            FROM items i
            WHERE i.id_empresa = :id_empresa
              AND i.id_item    = cast(:id_item as uuid)
              AND i.activo     = TRUE
        """)
        result = await self.db.execute(sql, {"id_empresa": id_empresa, "id_item": id_item})
        row = result.mappings().first()
        return dict(row) if row else None

    async def list_by_empresa(
        self,
        id_empresa: int,
        activo: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        """Devuelve (items, total) para listados administrativos."""
        sql = text("""
            SELECT
                i.id_item::text AS id_item, i.tipo, i.categoria, i.titulo,
                i.precio::float AS precio, i.moneda, i.activo, i.destacado,
                i.atributos, i.media, i.created_at
            FROM items i
            WHERE i.id_empresa = :id_empresa AND i.activo = :activo
            ORDER BY i.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        count_sql = text(
            "SELECT COUNT(*) FROM items i WHERE i.id_empresa = :id_empresa AND i.activo = :activo"
        )
        params = {"id_empresa": id_empresa, "activo": activo, "limit": limit, "offset": offset}
        rows = (await self.db.execute(sql, params)).mappings()
        total = (await self.db.execute(count_sql, {"id_empresa": id_empresa, "activo": activo})).scalar() or 0
        return [dict(r) for r in rows], total
