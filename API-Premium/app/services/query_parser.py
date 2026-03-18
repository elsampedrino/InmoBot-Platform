"""
QueryParser — traduce lenguaje natural a SearchFilters estructurados.

Responsabilidades:
- Detectar tipo, categoría, zona, precio, moneda y atributos del mensaje
- Normalizar sinónimos y variantes del lenguaje
- Combinar con filtros activos del contexto en caso de refinamiento
- Producir un SearchFilters listo para el SearchEngine

Debe funcionar principalmente con reglas y diccionarios.
Solo usar IA (Haiku) en fallback para casos ambiguos.

No debe:
- Decidir la ruta operativa
- Ejecutar búsquedas
- Generar texto al usuario
"""
from app.models.domain_models import ConversationState, SearchFilters


class QueryParser:

    async def parse(
        self,
        mensaje: str,
        state: ConversationState,
        is_refinement: bool = False,
    ) -> SearchFilters:
        """
        Parsea el mensaje y devuelve filtros estructurados.
        Si is_refinement=True, fusiona con los filters_activos del estado.
        """
        # TODO Fase 4
        raise NotImplementedError

    def _extract_tipo(self, mensaje: str) -> str | None:
        """Detecta el tipo de item (casa, departamento, campo, etc.)."""
        # TODO Fase 4
        raise NotImplementedError

    def _extract_zona(self, mensaje: str) -> str | None:
        """Detecta barrio, ciudad o zona geográfica."""
        # TODO Fase 4
        raise NotImplementedError

    def _extract_precio(self, mensaje: str) -> tuple[float | None, float | None, str | None]:
        """Devuelve (precio_min, precio_max, moneda)."""
        # TODO Fase 4
        raise NotImplementedError

    def _extract_atributos(self, mensaje: str) -> dict:
        """
        Detecta atributos dinámicos según el rubro:
        ambientes, dormitorios, pileta, cochera, etc.
        """
        # TODO Fase 4
        raise NotImplementedError

    def _merge_with_active_filters(
        self, new_filters: SearchFilters, active: dict
    ) -> SearchFilters:
        """
        Fusiona los filtros nuevos con los activos del contexto.
        Los nuevos tienen precedencia sobre los activos.
        """
        # TODO Fase 4
        raise NotImplementedError
