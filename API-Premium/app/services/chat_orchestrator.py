"""
ChatOrchestrator — orquestador del pipeline conversacional completo.

Pipeline Fase 3 (router real + context manager inteligente):
  1. TenantResolver       → carga empresa + rubro + configuración
  2. ContextManager       → carga o crea conversación + estado estructurado
  3. Persistir mensaje del usuario
  4. RouterConversacional → decide ruta por reglas determinísticas (Haiku como fallback)
  5. Actualizar estado conversacional con la decisión del router
  6. Generar respuesta (template contextualizado — Search Engine en Fase 4)
  7. Persistir mensaje del bot
  8. Actualizar estado_json y resumen en contextos_conversacion
  9. Devolver ChatMessageResponse

Pipeline completo (Fases 4+):
  → QueryParser → SearchEngine / KB → PromptService → AIService → ResponseAssembler → Analytics
"""
import time
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.api_models import ChatMessageRequest, ChatMessageResponse
from app.models.domain_models import (
    ConversationStage,
    ConversationState,
    Route,
    RouterDecision,
    TenantConfig,
)
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


class ChatOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.tenant_resolver = TenantResolver(db)
        self.context_manager = ContextManager(db)
        self.router = RouterConversacional()
        self.query_parser = QueryParser()
        self.search_engine = SearchEngine(db)
        self.kb_service = KBService(db)
        self.leads_service = LeadsService(db)
        self.prompt_service = PromptService()
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

            # ── Paso 4: Router conversacional real ─────────────────────────────
            decision = await self.router.decide(turn)

            # ── Paso 5: Actualizar estado con la decisión ──────────────────────
            new_state = self._advance_state(turn.conversation_state, decision)

            # ── Paso 6: Generar respuesta contextualizada ──────────────────────
            respuesta = self._build_response(decision, turn, tenant_config, new_state)

            # ── Paso 7: Persistir mensaje del bot ──────────────────────────────
            await self.context_manager.save_bot_message(
                id_conversacion=turn.id_conversacion,
                mensaje=respuesta,
            )

            # ── Paso 8: Actualizar contexto ────────────────────────────────────
            resumen = self._build_summary(new_state, request.mensaje, decision)
            await self.context_manager.update_context(
                id_conversacion=turn.id_conversacion,
                state=new_state,
                resumen=resumen,
            )

            elapsed_ms = int((time.monotonic() - start_ms) * 1000)
            logger.info(
                "turn_completed",
                session_id=request.session_id,
                empresa=request.empresa_slug,
                route=decision.route.value,
                intent=decision.intent,
                confidence=round(decision.confidence, 2),
                used_ai_fallback=decision.used_ai_fallback,
                stage=new_state.conversation_stage.value,
                response_time_ms=elapsed_ms,
            )

            return ChatMessageResponse(
                session_id=request.session_id,
                conversation_id=turn.id_conversacion,
                respuesta=respuesta,
                items=[],
                route=decision.route.value,
                stage=new_state.conversation_stage.value,
                lead_capturado=new_state.lead_capturado,
                metadata={
                    "response_time_ms": elapsed_ms,
                    "fase": 3,
                    "intent": decision.intent,
                    "confidence": round(decision.confidence, 2),
                    "used_ai_fallback": decision.used_ai_fallback,
                    "business_signals": decision.business_signals,
                },
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

    # ─── Estado conversacional ────────────────────────────────────────────────

    def _advance_state(
        self, state: ConversationState, decision: RouterDecision
    ) -> ConversationState:
        """
        Avanza el estado conversacional según la decisión del router.
        Actualiza flags de señales comerciales y esperas operativas.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        state.last_user_message_at = now_iso
        state.intent_previa = state.route_actual  # guardar intención anterior
        state.route_actual = decision.route.value

        # Transición de etapa: inicio → exploración en primer turno real
        if state.conversation_stage == ConversationStage.INICIO:
            state.conversation_stage = ConversationStage.EXPLORACION

        route = decision.route

        # Exploración
        if route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA, Route.PREGUNTA_KB):
            state.conversation_stage = ConversationStage.EXPLORACION
            # Limpiar esperas operativas si el usuario retoma búsqueda
            state.esperando_contacto = False
            state.esperando_visita = False

        # Interés en item específico
        if route == Route.VER_DETALLE_ITEM:
            state.conversation_stage = ConversationStage.INTERES
            item_ref = decision.entities.get("item_referenciado")
            if item_ref:
                state.ultimo_item_referenciado = item_ref

        # Conversión: contacto
        if route == Route.CONTACTAR_ASESOR:
            state.conversation_stage = ConversationStage.CONVERSION
            state.advisor_requested = True
            state.esperando_contacto = True

        # Conversión: visita
        if route == Route.AGENDAR_VISITA:
            state.conversation_stage = ConversationStage.CONVERSION
            state.visit_requested = True
            state.esperando_visita = True

        # Datos de contacto provistos: cerrar espera + marcar lead
        if decision.intent == "datos_de_contacto_provistos":
            state.lead_capturado = True
            state.esperando_contacto = False
            state.esperando_visita = False

        return state

    # ─── Respuestas contextualizadas ──────────────────────────────────────────

    def _build_response(
        self,
        decision: RouterDecision,
        turn,
        cfg: TenantConfig,
        state: ConversationState,
    ) -> str:
        """
        Genera una respuesta contextualizada basada en la ruta y el estado.
        Template enriquecido con contexto — AIService (Sonnet) en Fase 5.
        """
        route = decision.route
        nombre = cfg.nombre_empresa

        if route == Route.SALUDO:
            if decision.intent == "primer_mensaje":
                return (
                    f"¡Hola! Soy el asistente virtual de {nombre}. "
                    f"Estoy acá para ayudarte a encontrar la propiedad ideal. "
                    f"¿Qué tipo de propiedad estás buscando y en qué zona?"
                )
            return (
                f"¡Hola de nuevo! ¿En qué puedo ayudarte hoy? "
                f"Podés pedirme propiedades, filtrar por precio o zona, o consultar cualquier duda."
            )

        if route == Route.BUSCAR_CATALOGO:
            return (
                "Entendido, busco propiedades que se ajusten a lo que necesitás. "
                "[Búsqueda en catálogo disponible en Fase 4]. "
                "¿Tenés alguna preferencia de zona o rango de precio?"
            )

        if route == Route.REFINAR_BUSQUEDA:
            filtros = state.filters_activos
            detalle = (
                f" (filtros actuales: {', '.join(f'{k}: {v}' for k, v in filtros.items())})"
                if filtros
                else ""
            )
            return (
                f"Perfecto, ajusto los resultados con ese criterio{detalle}. "
                "[Refinamiento disponible en Fase 4]. "
                "¿Hay algo más que quieras cambiar?"
            )

        if route == Route.VER_DETALLE_ITEM:
            item_ref = decision.entities.get("item_referenciado")
            # Buscar título en items_recientes_resumen si existe
            titulo = None
            if item_ref:
                for it in state.items_recientes_resumen:
                    if it.id_item == item_ref:
                        titulo = it.titulo
                        break
            if titulo:
                return (
                    f"Te muestro más detalles de \"{titulo}\". "
                    "[Detalle completo disponible en Fase 4]. "
                    "¿Querés coordinar una visita o hablar con un asesor?"
                )
            return (
                "Te muestro más detalles de esa propiedad. "
                "[Detalle completo disponible en Fase 4]. "
                "¿Querés coordinar una visita o hablar con un asesor?"
            )

        if route == Route.CONTACTAR_ASESOR:
            if decision.intent == "datos_de_contacto_provistos":
                return (
                    "¡Perfecto! Ya recibimos tus datos. "
                    f"Un asesor de {nombre} se va a comunicar con vos a la brevedad. "
                    "¿Hay algo más en lo que pueda ayudarte?"
                )
            return (
                f"Con gusto te conecto con un asesor de {nombre}. "
                "¿Podés dejarnos tu nombre y número de teléfono para que se comuniquen a la brevedad?"
            )

        if route == Route.AGENDAR_VISITA:
            if decision.intent == "datos_de_contacto_provistos":
                return (
                    "¡Perfecto! Ya recibimos tus datos. "
                    f"Un asesor de {nombre} se va a comunicar con vos para confirmar la visita. "
                    "¿Hay algo más en lo que pueda ayudarte?"
                )
            return (
                "¡Genial que quieras conocer la propiedad en persona! "
                "Para coordinar la visita necesito tu nombre y número de contacto."
            )

        if route == Route.PREGUNTA_KB:
            return (
                "Esa es una muy buena pregunta. "
                "[Respuesta desde base de conocimiento disponible en Fase 6]. "
                f"Por ahora te recomiendo consultar directamente con {nombre} para obtener todos los detalles."
            )

        # FALLBACK
        return (
            "Entendido. ¿Podés contarme un poco más sobre lo que estás buscando? "
            "Así puedo ayudarte mejor."
        )

    # ─── Resumen del turno ────────────────────────────────────────────────────

    def _build_summary(
        self, state: ConversationState, mensaje: str, decision: RouterDecision
    ) -> str | None:
        """
        Genera un resumen textual del turno para resumen_contexto.
        Devuelve None en el primer turno (INICIO) donde no hay contexto aún.
        """
        if state.conversation_stage == ConversationStage.INICIO:
            return None

        stage_label = {
            ConversationStage.EXPLORACION: "explorando propiedades",
            ConversationStage.INTERES: "con interés en una propiedad específica",
            ConversationStage.CONVERSION: "en proceso de conversión (contacto/visita)",
            ConversationStage.CERRADA: "conversación cerrada",
        }.get(state.conversation_stage, "")

        filtros_str = (
            f" Filtros activos: {state.filters_activos}."
            if state.filters_activos
            else ""
        )
        signals_str = ""
        if state.advisor_requested:
            signals_str += " Solicitó asesor."
        if state.visit_requested:
            signals_str += " Solicitó visita."
        if state.lead_capturado:
            signals_str += " Lead capturado."

        return (
            f"El usuario está {stage_label}. "
            f"Última ruta: {decision.route.value} (intent: {decision.intent}). "
            f"Último mensaje: \"{mensaje[:120]}\".{filtros_str}{signals_str}"
        )