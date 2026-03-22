"""
SearchEngine — construye y ejecuta búsquedas en PostgreSQL.

Responsabilidades:
- Recibir SearchFilters del QueryParser
- Construir queries SQL dinámicas (filtros opcionales + JSONB para atributos)
- Rankear candidatos: destacado DESC, created_at DESC
- Devolver SearchResult con items candidatos y facetas básicas

Filtros JSONB soportados:
- atributos->>'barrio' / atributos->>'ciudad'   (zona, ILIKE)
- (atributos->>'ambientes')::int                (igual)
- (atributos->>'dormitorios')::int              (>=)
- atributos->'detalles' @> cast(... as jsonb)   (contiene, array)

Principio: "La base de datos es el motor de búsqueda."

No debe:
- Interpretar intención del usuario
- Redactar respuestas
- Manejar leads o followups
"""
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.domain_models import ItemCandidate, SearchFilters, SearchResult
from app.repositories.items_repository import ItemsRepository

logger = get_logger(__name__)

# ─── REGLA DE NEGOCIO: catálogo de inicio ────────────────────────────────────
# Si el parser no extrae filtros útiles (has_useful_filters() == False),
# no se vuelca el catálogo completo. Se devuelven como máximo este número
# de items activos, ordenados por destacado DESC, created_at DESC.
# Esto es independiente de MAX_ITEMS_PER_RESPONSE: aplica aunque ese setting
# se aumente en el futuro.
_MAX_ITEMS_NO_FILTERS = 5
# ─────────────────────────────────────────────────────────────────────────────


class SearchEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = ItemsRepository(db)

    async def search(
        self,
        id_empresa: int,
        id_rubro: int,
        filters: SearchFilters,
        limit: int = 5,
    ) -> SearchResult:
        """
        Ejecuta la búsqueda principal sobre la tabla items.
        Construye el WHERE dinámico según los filtros disponibles.

        Regla de negocio — catálogo de inicio:
            Si filters.has_useful_filters() == False (el usuario no especificó
            criterios útiles), se aplica _MAX_ITEMS_NO_FILTERS como tope,
            independientemente del 'limit' recibido.
            Esto evita volcar el catálogo completo sin contexto.
        """
        if not filters.has_useful_filters():
            effective_limit = min(limit, _MAX_ITEMS_NO_FILTERS)
            logger.info(
                "search_no_filters_applied",
                id_empresa=id_empresa,
                effective_limit=effective_limit,
            )
        else:
            effective_limit = limit

        clauses, params = self._build_where_clauses(filters)

        rows = await self._repo.search(
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            where_clauses=clauses,
            params=params,
            limit=effective_limit,
        )
        total = await self._repo.count(
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            where_clauses=clauses,
            params=params,
        )

        items = [self._row_to_candidate(row) for row in rows]
        facets = self._extract_facets(rows)

        logger.info(
            "search_executed",
            id_empresa=id_empresa,
            filters_tipo=filters.tipo,
            filters_categoria=filters.categoria,
            filters_zona=filters.zona,
            filters_atributos=filters.atributos,
            total_encontrados=total,
            devueltos=len(items),
        )

        return SearchResult(
            items=items,
            total_encontrados=total,
            facets=facets,
        )

    async def get_item_detail(self, id_empresa: int, id_item: str) -> dict | None:
        """Devuelve el detalle completo de un item por su ID."""
        row = await self._repo.get_by_id(id_empresa=id_empresa, id_item=id_item)
        if not row:
            logger.warning("item_not_found", id_empresa=id_empresa, id_item=id_item)
        return row

    # ─── Construcción del WHERE dinámico ──────────────────────────────────────

    def _build_where_clauses(self, filters: SearchFilters) -> tuple[list[str], dict]:
        """
        Construye lista de cláusulas WHERE y dict de parámetros.
        Los atributos JSONB usan operadores @> y ->>  con cast a jsonb.
        """
        clauses: list[str] = []
        params: dict = {}

        if filters.tipo:
            clauses.append("i.tipo = :tipo")
            params["tipo"] = filters.tipo

        if filters.categoria:
            clauses.append("i.categoria = :categoria")
            params["categoria"] = filters.categoria

        if filters.zona:
            clauses.append(
                "(i.atributos->>'barrio' ILIKE :zona OR i.atributos->>'ciudad' ILIKE :zona)"
            )
            params["zona"] = f"%{filters.zona}%"

        if filters.precio_max is not None:
            # Incluir propiedades sin precio (precio 0 o NULL → consultar igual)
            clauses.append(
                "(i.precio IS NULL OR i.precio = 0 OR i.precio <= :precio_max)"
            )
            params["precio_max"] = filters.precio_max

        if filters.precio_min is not None:
            clauses.append("i.precio >= :precio_min")
            params["precio_min"] = filters.precio_min

        # Atributos JSONB: reglas específicas de inmobiliaria
        atrib_clauses, atrib_params = self._build_atributo_clauses(filters.atributos)
        clauses.extend(atrib_clauses)
        params.update(atrib_params)

        return clauses, params

    def _build_atributo_clauses(
        self, atributos: dict
    ) -> tuple[list[str], dict]:
        """
        Traduce el dict de atributos de inmuebles a cláusulas JSONB.

        Reglas de negocio (documentadas también en query_parser.py):
          - ambientes:    match EXACTO (=)
                          "2 ambientes" ≠ "3 ambientes" en inmobiliaria argentina.
          - dormitorios:  match MÍNIMO (>=)
                          "2 dormitorios" incluye propiedades con 3 o más.
          - booleanos:    @> contains sobre el array atributos->'detalles'
                          Ej: pileta=True → atributos->'detalles' debe contener "pileta".
        """
        clauses: list[str] = []
        params: dict = {}

        for key, val in atributos.items():
            if key == "ambientes" and isinstance(val, int):
                # Exacto: el usuario pidió N ambientes específicos
                clauses.append(
                    "(i.atributos->>'ambientes') IS NOT NULL "
                    "AND (i.atributos->>'ambientes')::int = :ambientes"
                )
                params["ambientes"] = val

            elif key == "dormitorios" and isinstance(val, int):
                # Mínimo: "2 dormitorios" satisface 2, 3, 4...
                clauses.append(
                    "(i.atributos->>'dormitorios') IS NOT NULL "
                    "AND (i.atributos->>'dormitorios')::int >= :dormitorios"
                )
                params["dormitorios"] = val

            elif isinstance(val, bool) and val:
                # Detalle booleano: el array JSON debe contener el string
                pname = f"det_{key}"
                clauses.append(
                    f"i.atributos->'detalles' @> cast(:{pname} as jsonb)"
                )
                params[pname] = json.dumps([key])

        return clauses, params

    # ─── Conversión de filas ───────────────────────────────────────────────────

    def _row_to_candidate(self, row: dict) -> ItemCandidate:
        atributos = row.get("atributos") or {}
        if isinstance(atributos, str):
            atributos = json.loads(atributos)

        media = row.get("media") or {}
        if isinstance(media, str):
            media = json.loads(media)

        fotos = media.get("fotos", []) if isinstance(media, dict) else []

        return ItemCandidate(
            id_item=row["id_item"],
            titulo=row["titulo"],
            descripcion_corta=row.get("descripcion_corta"),
            precio=row.get("precio"),
            moneda=row.get("moneda"),
            atributos=atributos,
            fotos=fotos,
            destacado=row.get("destacado", False),
        )

    # ─── Facetas ──────────────────────────────────────────────────────────────

    def _extract_facets(self, rows: list[dict]) -> dict:
        """
        Extrae facetas básicas de los resultados para sugerencias de refinamiento.
        """
        tipos: dict[str, int] = {}
        zonas: dict[str, int] = {}

        for row in rows:
            t = row.get("tipo")
            if t:
                tipos[t] = tipos.get(t, 0) + 1

            atrib = row.get("atributos") or {}
            if isinstance(atrib, str):
                import json as _json
                atrib = _json.loads(atrib)
            barrio = atrib.get("barrio") if isinstance(atrib, dict) else None
            if barrio:
                zonas[barrio] = zonas.get(barrio, 0) + 1

        return {"tipos": tipos, "zonas": zonas}
