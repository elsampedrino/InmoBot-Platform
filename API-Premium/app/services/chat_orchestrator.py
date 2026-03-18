"""
ChatOrchestrator — orquestador del pipeline conversacional completo.

Pipeline por turno (Fase 2 — mínimo funcional):
  1. TenantResolver    → carga empresa + rubro + configuración
  2. ContextManager    → carga o crea conversación + estado estructurado
  3. Persistir mensaje del usuario
  4. Generar respuesta (dummy controlado en Fase 2)
  5. Avanzar estado conversacional básico
  6. Persistir mensaje del bot
  7. Actualizar estado_json en contextos_conversacion
  8. Devolver ChatMessageResponse

Pipeline completo (Fases 3+):
  → Router Conversacional → Parser → Search Engine / KB / Leads
  → Prompt Service → AI Service → Response Assembler → Analytics
"""
import time
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.api_models import ChatMessageRequest, ChatMessageResponse
from app.models.domain_models import ConversationStage, ConversationState, Route, TenantConfig
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.context_manager import ContextManager
from app.services.kb_service import KBService
from app.services.leads_service import LeadsService
from app.services.prompt_service import PromptService
from app.services.query_parser import QueryParser
from app.services.response_assembler import ResponseAssembler
from app.services.router_conversacional import RouterConversacional
from app.services.search_engine import SearchEngine
from app.services.tenant_resolver import TenantResolver

logger = get_logger(__name__)

# ─── Keywords para clasificación dummy ────────────────────────────────────────
_GREETING_WORDS = {
    "hola", "buenas", "buenos", "buen", "hi", "hello", "saludos", "hey",
    "que tal", "qué tal", "como estas", "cómo estás",
}
_SEARCH_WORDS = {
    "busco", "buscar", "quiero", "necesito", "tenés", "tienen", "hay",
    "mostrame", "muéstrame", "ver", "casas", "departamentos", "lotes",
    "campos", "propiedad", "propiedades",
}
_CONTACT_WORDS = {
    "contactar", "llamar", "asesor", "teléfono", "telefono", "celular",
    "whatsapp", "email", "correo", "quiero hablar", "me interesa",
}
_VISIT_WORDS = {
    "visitar", "visita", "conocer", "ver en persona", "coordinar",
    "cuando puedo", "cuándo puedo", "sacar turno",
}


class ChatOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.tenant_resolver = TenantResolver(db)
        self.context_manager = ContextManager(db)
        # Fases 3+: se implementan progresivamente
        self.router = RouterConversacional()
        self.query_parser = QueryParser()
        self.search_engine = SearchEngine(db)
        self.kb_service = KBService(db)
        self.leads_service = LeadsService(db)
        self.prompt_service = PromptService()
        self.ai_service = AIService()
        self.response_assembler = ResponseAssembler()
        self.analytics_service = AnalyticsService(db)

    # ─── Pipeline principal ───────────────────────────────────────────────────

    async def handle_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        start_ms = time.monotonic()

        try:
            # ── Paso 1: Resolver tenant ────────────────────────────────────────
            tenant_config = await self.tenant_resolver.resolve(request.empresa_slug)

            # ── Paso 2: Cargar contexto del turno ──────────────────────────────
            turn = await self.context_manager.load_turn_context(
                id_empresa=tenant_config.id_empresa,
                id_rubro=tenant_config.id_rubro,
                canal=request.canal,
                session_id=request.session_id,
                mensaje=request.mensaje,
                tenant_config=tenant_config,
            )

            # ── Paso 3: Persistir mensaje del usuario ──────────────────────────
            await self.context_manager.save_user_message(
                id_conversacion=turn.id_conversacion,
                mensaje=request.mensaje,
                raw_payload=request.metadata,
            )

            # ── Paso 4: Clasificar y generar respuesta (dummy Fase 2) ──────────
            route, respuesta = self._dummy_pipeline(
                mensaje=request.mensaje,
                state=turn.conversation_state,
                tenant_config=tenant_config,
            )

            # ── Paso 5: Avanzar estado conversacional básico ───────────────────
            new_state = self._advance_state(
                state=turn.conversation_state,
                route=route,
            )

            # ── Paso 6: Persistir mensaje del bot ──────────────────────────────
            await self.context_manager.save_bot_message(
                id_conversacion=turn.id_conversacion,
                mensaje=respuesta,
            )

            # ── Paso 7: Actualizar contexto ────────────────────────────────────
            await self.context_manager.update_context(
                id_conversacion=turn.id_conversacion,
                state=new_state,
                resumen=self._build_basic_summary(turn.conversation_state, request.mensaje, route),
            )

            elapsed_ms = int((time.monotonic() - start_ms) * 1000)
            logger.info(
                "turn_completed",
                session_id=request.session_id,
                empresa=request.empresa_slug,
                route=route.value,
                stage=new_state.conversation_stage.value,
                response_time_ms=elapsed_ms,
            )

            return ChatMessageResponse(
                session_id=request.session_id,
                conversation_id=turn.id_conversacion,
                respuesta=respuesta,
                items=[],
                route=route.value,
                stage=new_state.conversation_stage.value,
                lead_capturado=new_state.lead_capturado,
                metadata={"response_time_ms": elapsed_ms, "fase": 2},
            )

        except HTTPException:
            raise
        except Exception as exc:
            logger.error(
                "orchestrator_error",
                empresa=request.empresa_slug,
                session_id=request.session_id,
                error=str(exc),
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Error interno del asistente.") from exc

    # ─── Clasificación dummy (Fase 2) ─────────────────────────────────────────

    def _dummy_pipeline(
        self,
        mensaje: str,
        state: ConversationState,
        tenant_config: TenantConfig,
    ) -> tuple[Route, str]:
        """
        Clasificación simplificada y respuesta dummy para Fase 2.
        Detecta la intención con keywords y devuelve un texto controlado.
        El Router Conversacional real reemplazará esto en Fase 3.
        """
        route = self._classify_route_dummy(mensaje, state)
        respuesta = self._build_dummy_response(route, mensaje, tenant_config)
        return route, respuesta

    def _classify_route_dummy(
        self, mensaje: str, state: ConversationState
    ) -> Route:
        """
        Clasificación por keywords. Aplica prioridad igual que el router real:
        visita > contacto > búsqueda > saludo > fallback.
        """
        words = set(mensaje.lower().split())

        # Primer mensaje siempre es saludo si no hay contexto previo
        if state.conversation_stage == ConversationStage.INICIO:
            return Route.SALUDO

        if words & _VISIT_WORDS:
            return Route.AGENDAR_VISITA
        if words & _CONTACT_WORDS:
            return Route.CONTACTAR_ASESOR
        if words & _SEARCH_WORDS:
            return Route.BUSCAR_CATALOGO
        if words & _GREETING_WORDS:
            return Route.SALUDO

        return Route.FALLBACK

    def _build_dummy_response(
        self, route: Route, mensaje: str, cfg: TenantConfig
    ) -> str:
        """
        Respuestas dummy por ruta. Reemplazado por AIService en Fase 5.
        """
        nombre = cfg.nombre_empresa

        responses = {
            Route.SALUDO: (
                f"¡Hola! Soy el asistente virtual de {nombre}. "
                f"Estoy aquí para ayudarte a encontrar la propiedad ideal. "
                f"¿Qué tipo de propiedad estás buscando y en qué zona?"
            ),
            Route.BUSCAR_CATALOGO: (
                f"Entendido, voy a buscar propiedades que se ajusten a lo que necesitás. "
                f"[Búsqueda real disponible en Fase 4 — Search Engine]. "
                f"¿Tenés alguna preferencia de zona o precio?"
            ),
            Route.REFINAR_BUSQUEDA: (
                "Perfecto, voy a ajustar los resultados con ese filtro. "
                "[Refinamiento disponible en Fase 4]."
            ),
            Route.VER_DETALLE_ITEM: (
                "Te muestro más detalles de esa propiedad. "
                "[Detalle disponible en Fase 4]."
            ),
            Route.CONTACTAR_ASESOR: (
                f"Claro, con gusto te pongo en contacto con un asesor de {nombre}. "
                f"¿Podés dejarnos tu nombre y teléfono para que se comuniquen a la brevedad?"
            ),
            Route.AGENDAR_VISITA: (
                "¡Genial! Para coordinar la visita necesito algunos datos. "
                "¿Cuál es tu nombre y teléfono de contacto?"
            ),
            Route.PREGUNTA_KB: (
                f"Esa es una excelente pregunta. "
                f"[Respuesta desde Knowledge Base disponible en Fase 6]. "
                f"Por ahora te recomiendo contactar directamente a {nombre}."
            ),
            Route.FALLBACK: (
                "Entendido. ¿Podés contarme un poco más sobre lo que estás buscando? "
                "Así puedo ayudarte mejor."
            ),
        }
        return responses.get(route, responses[Route.FALLBACK])

    # ─── Estado conversacional ────────────────────────────────────────────────

    def _advance_state(
        self, state: ConversationState, route: Route
    ) -> ConversationState:
        """
        Avanza el estado conversacional según la ruta detectada.
        Lógica básica para Fase 2; el ContextManager completo llega en Fase 3.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        state.last_user_message_at = now_iso
        state.route_actual = route.value

        # Transiciones de etapa
        if state.conversation_stage == ConversationStage.INICIO:
            state.conversation_stage = ConversationStage.EXPLORACION

        if route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA, Route.VER_DETALLE_ITEM):
            state.conversation_stage = ConversationStage.EXPLORACION

        if route == Route.VER_DETALLE_ITEM:
            state.conversation_stage = ConversationStage.INTERES

        if route in (Route.CONTACTAR_ASESOR, Route.AGENDAR_VISITA, Route.CAPTURAR_LEAD):
            state.conversation_stage = ConversationStage.CONVERSION
            state.advisor_requested = route == Route.CONTACTAR_ASESOR
            state.visit_requested = route == Route.AGENDAR_VISITA
            state.esperando_contacto = True

        return state

    def _build_basic_summary(
        self, state: ConversationState, mensaje: str, route: Route
    ) -> str | None:
        """
        Genera un resumen textual básico del turno para resumen_contexto.
        El ContextManager con IA lo mejorará en Fases siguientes.
        Devuelve None si la etapa es INICIO (no hay nada relevante aún).
        """
        if state.conversation_stage == ConversationStage.INICIO:
            return None

        stage_label = {
            ConversationStage.EXPLORACION: "explorando propiedades",
            ConversationStage.INTERES: "con interés en una propiedad específica",
            ConversationStage.CONVERSION: "en proceso de conversión (contacto/visita)",
            ConversationStage.CERRADA: "conversación cerrada",
        }.get(state.conversation_stage, "")

        return (
            f"El usuario está {stage_label}. "
            f"Última intención: {route.value}. "
            f"Último mensaje: \"{mensaje[:120]}\""
        )
