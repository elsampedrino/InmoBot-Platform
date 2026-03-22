"""
AIService — integración controlada con Claude (Haiku + Sonnet).

Responsabilidades:
- Invocar Haiku para clasificación de intención (fallback del router)
- Invocar Sonnet para redacción de respuesta conversacional final
- Devolver salidas estructuradas o texto según el caso
- Registrar tokens y latencia para analítica

Principio: "La IA no busca, la IA explica."
La IA es el último paso, no el núcleo del sistema.

No debe:
- Reemplazar al router ni al parser determinístico
- Decidir la arquitectura del flujo
- Acceder a datos sin contexto ya preparado
"""
import json
import time

import anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.models.domain_models import ConversationState, Route

logger = get_logger(__name__)

_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


class AIService:

    async def classify_intent(
        self,
        mensaje: str,
        state: ConversationState,
        candidate_routes: list[Route],
    ) -> dict:
        """
        Usa Haiku para clasificar la intención cuando las reglas no alcanzan.
        Devuelve: {"route": Route, "intent": str, "confidence": float, "entities": dict}
        """
        routes_str = ", ".join(r.value for r in candidate_routes)
        has_active_search = bool(state.filters_activos or state.items_recientes)

        system = f"""Sos un clasificador de intención para un chatbot inmobiliario argentino.
Analizá el mensaje del usuario y determiná la ruta más apropiada.

Rutas disponibles: {routes_str}

Contexto actual:
- Etapa: {state.conversation_stage.value}
- Ruta anterior: {state.route_actual or "ninguna"}
- Búsqueda activa: {"sí" if has_active_search else "no"}
- Items mostrados previamente: {len(state.items_recientes)}
- Esperando contacto: {"sí" if state.esperando_contacto else "no"}
- Esperando visita: {"sí" if state.esperando_visita else "no"}

Respondé ÚNICAMENTE con JSON válido en este formato exacto, sin texto adicional:
{{
  "route": "<ruta elegida de las disponibles>",
  "intent": "<descripción breve de la intención en español>",
  "confidence": <número entre 0.0 y 1.0>,
  "entities": {{}}
}}"""

        result = await self._call_haiku(
            system=system,
            messages=[{"role": "user", "content": mensaje}],
            max_tokens=200,
        )

        try:
            data = json.loads(result["content"])
            route_value = data.get("route", Route.FALLBACK.value)
            try:
                route = Route(route_value)
            except ValueError:
                route = Route.FALLBACK

            logger.debug(
                "haiku_intent_classified",
                route=route.value,
                confidence=data.get("confidence"),
                tokens_input=result["tokens_input"],
                tokens_output=result["tokens_output"],
                response_time_ms=result["response_time_ms"],
            )

            return {
                "route": route,
                "intent": data.get("intent", "desconocido"),
                "confidence": float(data.get("confidence", 0.5)),
                "entities": data.get("entities", {}),
            }
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("haiku_intent_parse_error", error=str(exc), raw=result["content"])
            return {
                "route": Route.FALLBACK,
                "intent": "clasificación_fallida",
                "confidence": 0.0,
                "entities": {},
            }

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[dict],
    ) -> dict:
        """
        Usa Sonnet para redactar la respuesta conversacional final.
        Devuelve: {"text": str, "tokens_input": int, "tokens_output": int, "response_time_ms": int}
        """
        # TODO Fase 5
        raise NotImplementedError

    async def _call_haiku(self, system: str, messages: list[dict], max_tokens: int = 512) -> dict:
        """Llamada directa a Haiku. Registra latencia y tokens."""
        start = time.monotonic()
        response = await _client.messages.create(
            model=settings.HAIKU_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return {
            "content": response.content[0].text,
            "tokens_input": response.usage.input_tokens,
            "tokens_output": response.usage.output_tokens,
            "response_time_ms": elapsed_ms,
        }

    async def _call_sonnet(self, system: str, messages: list[dict], max_tokens: int = 1024) -> dict:
        """Llamada directa a Sonnet. Registra latencia y tokens."""
        start = time.monotonic()
        response = await _client.messages.create(
            model=settings.SONNET_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return {
            "content": response.content[0].text,
            "tokens_input": response.usage.input_tokens,
            "tokens_output": response.usage.output_tokens,
            "response_time_ms": elapsed_ms,
        }
