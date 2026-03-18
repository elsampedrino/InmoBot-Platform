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
        # TODO Fase 5
        raise NotImplementedError

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
