"""
SearchEngine — construye y ejecuta búsquedas en PostgreSQL.

Responsabilidades:
- Recibir SearchFilters del QueryParser
- Construir queries SQL dinámicas (con filtros opcionales sobre atributos JSONB)
- Aprovechar índices: btree en (id_empresa, id_rubro, tipo), GIN en atributos
- Rankear candidatos (destacado > coincidencia > recencia)
- Devolver SearchResult con items candidatos y facetas

Principio: "La base de datos es el motor de búsqueda."

No debe:
- Interpretar intención del usuario
- Redactar respuestas
- Manejar leads o followups
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_models import SearchFilters, SearchResult


class SearchEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

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
        """
        # TODO Fase 4
        raise NotImplementedError

    async def get_item_detail(self, id_empresa: int, id_item: str) -> dict | None:
        """Devuelve el detalle completo de un item por su ID."""
        # TODO Fase 4
        raise NotImplementedError

    def _build_where_clauses(self, filters: SearchFilters) -> tuple[list, dict]:
        """
        Construye lista de cláusulas WHERE y dict de parámetros.
        Los atributos JSONB se filtran con operadores ->> y ::type.
        """
        # TODO Fase 4
        raise NotImplementedError

    def _rank_results(self, items: list[dict]) -> list[dict]:
        """
        Aplica ranking post-SQL:
        1. destacado (bool)
        2. score de coincidencia de atributos
        3. created_at DESC (recencia)
        """
        # TODO Fase 4
        raise NotImplementedError

    def _extract_facets(self, items: list[dict]) -> dict:
        """
        Extrae facetas de los resultados para sugerencias de refinamiento.
        Ej: {"barrios": {"Palermo": 3, "Belgrano": 2}, "tipos": {...}}
        """
        # TODO Fase 4
        raise NotImplementedError
