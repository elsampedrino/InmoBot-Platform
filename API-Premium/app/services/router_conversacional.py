"""
RouterConversacional — decide la ruta operativa de cada turno.

Responsabilidades:
- Clasificar la intención del mensaje usando reglas determinísticas
- Usar el contexto conversacional para resolver referencias y refinamientos
- Invocar Haiku solo como fallback cuando las reglas no son suficientes
- Devolver una RouterDecision con acciones explícitas

Prioridad de rutas (de mayor a menor):
  1. agendar_visita
  2. contactar_asesor
  3. capturar_lead
  4. ver_detalle_item
  5. refinar_busqueda
  6. buscar_catalogo
  7. pregunta_kb
  8. informacion_empresa
  9. saludo
  10. fallback

No debe:
- Parsear filtros detallados (eso es del QueryParser)
- Ejecutar búsquedas SQL
- Redactar respuestas finales
"""
from app.models.domain_models import ConversationState, Route, RouterDecision, TurnContext
from app.services.ai_service import AIService


class RouterConversacional:
    def __init__(self) -> None:
        self.ai_service = AIService()

    async def decide(self, turn: TurnContext) -> RouterDecision:
        """
        Decide la ruta operativa para el turno actual.
        Primero aplica reglas determinísticas, luego Haiku como fallback.
        """
        # TODO Fase 3
        raise NotImplementedError

    def _apply_rules(self, mensaje: str, state: ConversationState) -> RouterDecision | None:
        """
        Aplica reglas determinísticas sobre el mensaje y el estado.
        Devuelve None si las reglas no logran clasificar con suficiente confianza.
        """
        # TODO Fase 3
        raise NotImplementedError

    async def _classify_with_haiku(self, mensaje: str, state: ConversationState) -> RouterDecision:
        """
        Fallback: usa Haiku para clasificar la intención cuando las reglas no alcanzan.
        Solo se invoca si _apply_rules devuelve None.
        """
        # TODO Fase 3
        raise NotImplementedError

    def _resolve_refinement(self, mensaje: str, state: ConversationState) -> bool:
        """
        Detecta si el mensaje es un refinamiento de búsqueda previa
        (ej: "más barato", "con balcón", "en otra zona").
        """
        # TODO Fase 3
        raise NotImplementedError

    def _resolve_item_reference(self, mensaje: str, state: ConversationState) -> str | None:
        """
        Resuelve referencias a items previos ("el primero", "ese", "la opción 2").
        Devuelve el id_item referenciado o None.
        """
        # TODO Fase 3
        raise NotImplementedError
