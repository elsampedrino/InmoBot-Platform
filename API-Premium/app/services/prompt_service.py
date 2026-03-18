"""
PromptService — construcción dinámica del prompt final para la IA.

Responsabilidades:
- Combinar system_prompt del rubro + brand_voice + prompt_extra de empresa
- Incorporar el contexto conversacional (resumen + mensajes recientes)
- Inyectar los items candidatos del search engine en formato estructurado
- Inyectar fragmentos de KB cuando corresponda
- Devolver el prompt final listo para AIService

No debe:
- Decidir qué flujo ejecutar
- Consultar directamente el catálogo
- Medir analítica
"""
from app.models.domain_models import ItemCandidate, TenantConfig, TurnContext


class PromptService:

    def build_search_prompt(
        self,
        turn: TurnContext,
        items: list[ItemCandidate],
        facets: dict,
    ) -> tuple[str, list[dict]]:
        """
        Construye el system prompt y el historial de mensajes para responder
        una búsqueda de catálogo.
        Devuelve (system_prompt, messages) listos para la API de Anthropic.
        """
        # TODO Fase 5
        raise NotImplementedError

    def build_kb_prompt(
        self,
        turn: TurnContext,
        kb_chunks: list[dict],
    ) -> tuple[str, list[dict]]:
        """
        Construye el prompt para responder una pregunta sobre la KB.
        """
        # TODO Fase 5
        raise NotImplementedError

    def build_saludo_prompt(self, turn: TurnContext) -> tuple[str, list[dict]]:
        """Prompt para el mensaje de bienvenida inicial."""
        # TODO Fase 5
        raise NotImplementedError

    def build_lead_capture_prompt(self, turn: TurnContext) -> tuple[str, list[dict]]:
        """Prompt para solicitar datos de contacto al usuario."""
        # TODO Fase 5
        raise NotImplementedError

    def build_fallback_prompt(self, turn: TurnContext) -> tuple[str, list[dict]]:
        """Prompt para el caso fallback — mensaje no clasificado."""
        # TODO Fase 5
        raise NotImplementedError

    def _compose_system(self, config: TenantConfig) -> str:
        """
        Ensambla el system prompt base:
        system_prompt + style_prompt + brand_voice + prompt_extra
        """
        # TODO Fase 5
        raise NotImplementedError

    def _format_items_for_prompt(self, items: list[ItemCandidate]) -> str:
        """Serializa items como texto estructurado para el prompt."""
        # TODO Fase 5
        raise NotImplementedError
