"""
ItemsRepository — acceso a la tabla items (catálogo).

Responsabilidades:
- Búsquedas filtradas con WHERE dinámico (incluyendo JSONB)
- Lookup por id_item
- Listados administrativos paginados
"""
import json
import uuid
from typing import Any

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

    # ── Admin CRUD ────────────────────────────────────────────────────────────

    def _item_to_dict(self, item: Item) -> dict:
        return {
            "id_item": str(item.id_item),
            "id_empresa": item.id_empresa,
            "id_rubro": item.id_rubro,
            "external_id": item.external_id,
            "tipo": item.tipo,
            "categoria": item.categoria,
            "titulo": item.titulo,
            "descripcion": item.descripcion,
            "descripcion_corta": item.descripcion_corta,
            "precio": float(item.precio) if item.precio is not None else None,
            "moneda": item.moneda,
            "activo": item.activo,
            "destacado": item.destacado,
            "atributos": item.atributos or {},
            "media": item.media or {},
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }

    async def admin_list(
        self,
        id_empresa: int,
        activo: bool | None,
        tipo: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        """Lista items con filtros opcionales — incluye inactivos."""
        clauses = ["id_empresa = :id_empresa"]
        params: dict[str, Any] = {"id_empresa": id_empresa}
        if activo is not None:
            clauses.append("activo = :activo")
            params["activo"] = activo
        if tipo:
            clauses.append("tipo = :tipo")
            params["tipo"] = tipo

        where = " AND ".join(clauses)
        sql = text(f"""
            SELECT
                id_item::text, external_id, tipo, categoria, titulo,
                descripcion, descripcion_corta,
                precio::float AS precio, moneda, activo, destacado,
                atributos, media, created_at
            FROM items
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        count_sql = text(f"SELECT COUNT(*) FROM items WHERE {where}")
        params_page = {**params, "limit": limit, "offset": offset}
        rows = (await self.db.execute(sql, params_page)).mappings()
        total = (await self.db.execute(count_sql, params)).scalar() or 0
        return [dict(r) for r in rows], total

    async def admin_get(self, id_empresa: int, id_item: str) -> dict | None:
        """Devuelve item por id_item (incluye inactivos)."""
        sql = text("""
            SELECT
                id_item::text, external_id, tipo, categoria, titulo,
                descripcion, descripcion_corta,
                precio::float AS precio, moneda, activo, destacado,
                atributos, media, created_at
            FROM items
            WHERE id_empresa = :id_empresa AND id_item = cast(:id_item as uuid)
        """)
        row = (await self.db.execute(sql, {"id_empresa": id_empresa, "id_item": id_item})).mappings().first()
        return dict(row) if row else None

    async def admin_create(
        self,
        id_empresa: int,
        id_rubro: int,
        data: dict,
    ) -> dict:
        """Crea un nuevo item."""
        item = Item(
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            external_id=data["external_id"],
            tipo=data["tipo"],
            categoria=data.get("categoria"),
            titulo=data["titulo"],
            descripcion=data.get("descripcion"),
            descripcion_corta=data.get("descripcion_corta"),
            precio=data.get("precio"),
            moneda=data.get("moneda"),
            destacado=data.get("destacado", False),
            activo=True,
            atributos=data.get("atributos", {}),
            media={"fotos": data.get("fotos", [])},
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return self._item_to_dict(item)

    async def admin_update(
        self,
        id_empresa: int,
        id_item: str,
        data: dict,
    ) -> dict | None:
        """Actualiza campos de un item existente."""
        result = await self.db.execute(
            select(Item).where(
                Item.id_empresa == id_empresa,
                Item.id_item == uuid.UUID(id_item),
            )
        )
        item = result.scalar_one_or_none()
        if item is None:
            return None
        # Actualizar campos escalares
        scalar_fields = {
            "external_id", "tipo", "categoria", "titulo", "descripcion",
            "descripcion_corta", "precio", "moneda", "activo", "destacado",
        }
        for field in scalar_fields:
            if field in data and data[field] is not None:
                setattr(item, field, data[field])
        if "atributos" in data and data["atributos"] is not None:
            item.atributos = data["atributos"]
        if "fotos" in data and data["fotos"] is not None:
            item.media = {"fotos": data["fotos"]}
        await self.db.commit()
        await self.db.refresh(item)
        return self._item_to_dict(item)

    async def admin_toggle_activo(
        self,
        id_empresa: int,
        id_item: str,
        activo: bool,
    ) -> dict | None:
        """Activa o desactiva un item."""
        result = await self.db.execute(
            select(Item).where(
                Item.id_empresa == id_empresa,
                Item.id_item == uuid.UUID(id_item),
            )
        )
        item = result.scalar_one_or_none()
        if item is None:
            return None
        item.activo = activo
        await self.db.commit()
        await self.db.refresh(item)
        return self._item_to_dict(item)

    async def admin_list_activos_export(self, id_empresa: int) -> list[dict]:
        """Devuelve todos los items activos para exportar a landing."""
        sql = text("""
            SELECT
                id_item::text, external_id, tipo, categoria, titulo,
                descripcion, descripcion_corta,
                precio::float AS precio, moneda, activo, destacado,
                atributos, media
            FROM items
            WHERE id_empresa = :id_empresa AND activo = TRUE
            ORDER BY external_id ASC
        """)
        rows = (await self.db.execute(sql, {"id_empresa": id_empresa})).mappings()
        return [dict(r) for r in rows]
