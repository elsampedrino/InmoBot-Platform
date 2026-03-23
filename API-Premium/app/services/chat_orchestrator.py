"""
ChatOrchestrator — orquestador del pipeline conversacional completo.

Pipeline Fase 6b (Leads + Analytics):
  1. TenantResolver       → empresa + rubro + config
  2. ContextManager       → conversación + estado estructurado
  3. Persistir mensaje del usuario
  4. RouterConversacional → ruta por reglas (Haiku fallback)
  5. QueryParser          → SearchFilters (si la ruta requiere búsqueda)
  6. SearchEngine / KB    → resultados reales del catálogo o KB
  7. Actualizar estado conversacional
  8a. PromptService       → (system_prompt, messages) para Sonnet
  8b. AIService (Sonnet)  → redacción conversacional final
  8c. Fallback determinístico si Sonnet falla o está deshabilitado
  9. Persistir mensaje del bot
 10. Actualizar contexto (filters_activos, items_recientes, resumen)
 11. Captura de lead (si router señaló create_or_update_lead)
 12. Analytics: log_chat_turn + log_conversion_event (si aplica)
 13. Devolver ChatMessageResponse con items

Reglas de fallback:
  - ia_habilitada=False en TenantConfig → siempre usa plantilla
  - Sonnet timeout / error de API     → usa plantilla + log explícito
  - Fallo en lead capture / analytics → warning en log, pipeline continúa
"""
import re
import time
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.api_models import ChatMessageRequest, ChatMessageResponse, ItemBrief
from app.models.domain_models import (
    ConversionEvent,
    ConversationStage,
    ConversationState,
    ItemCandidate,
    ItemSummary,
    Route,
    RouterDecision,
    SearchFilters,
    SearchResult,
    TenantConfig,
)
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

# ─── Helper: extracción de datos de contacto ─────────────────────────────────
_RE_TELEFONO = re.compile(r"\+?[\d][\d\s\-\.]{5,14}")
_RE_EMAIL = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Detecta nombre solo cuando hay frase explícita de presentación.
# Captura palabras hasta la primera coma, "y", "mi", "tel(éfono)", "mail/email"
# o fin de cadena — sin consumir el delimitador (lookahead).
_RE_NOMBRE = re.compile(
    r"(?:me llamo|mi nombre es|mi nombre:|soy)\s+"
    r"([A-Za-záéíóúñÁÉÍÓÚÑüÜ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑüÜ]+)*?)"
    r"(?=\s*[,;]|\s+y\b|\s+mi\b|\s+tel|\s+mail|\s+email|$)",
    re.IGNORECASE,
)


def _parse_contact_data(text: str) -> tuple[str | None, str | None, str | None]:
    """
    Extracción best-effort de (nombre, telefono, email) de texto libre.
    Nunca lanza excepción; retorna None para los campos que no pudo extraer.

    Nombre: solo se extrae si hay frase explícita ("me llamo X", "soy X",
    "mi nombre es X"). Si no hay patrón reconocible, nombre = None en lugar
    de guardar el texto completo del mensaje.
    """
    # Email
    email_match = _RE_EMAIL.search(text)
    email = email_match.group(0) if email_match else None

    # Teléfono (sin cambios — funciona correctamente)
    phone_match = _RE_TELEFONO.search(text)
    telefono = re.sub(r"[\s\-\.]", "", phone_match.group(0)) if phone_match else None

    # Nombre: solo extraer si el usuario se presentó explícitamente
    nombre: str | None = None
    nombre_match = _RE_NOMBRE.search(text)
    if nombre_match:
        raw = nombre_match.group(1).strip()
        # Normalizar: eliminar espacios dobles y capitalizar cada inicial
        nombre = " ".join(w.capitalize() for w in raw.split()) or None
        if nombre and len(nombre) < 3:
            nombre = None

    return nombre, telefono, email


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
        self.ai_service = AIService()
        self.response_assembler = ResponseAssembler()
        self.analytics_service = AnalyticsService(db)

    # ─── Pipeline principal ───────────────────────────────────────────────────

    async def handle_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        start_ms = time.monotonic()

        try:
            # ── 1. Tenant ──────────────────────────────────────────────────────
            tenant_config = await self.tenant_resolver.resolve(request.empresa_slug)

            # ── 2. Contexto del turno ──────────────────────────────────────────
            turn = await self.context_manager.load_turn_context(
                id_empresa=tenant_config.id_empresa,
                id_rubro=tenant_config.id_rubro,
                canal=request.canal,
                session_id=request.session_id,
                mensaje=request.mensaje,
                tenant_config=tenant_config,
            )

            # ── 3. Persistir mensaje del usuario ───────────────────────────────
            await self.context_manager.save_user_message(
                id_conversacion=turn.id_conversacion,
                mensaje=request.mensaje,
                raw_payload=request.metadata,
            )

            # ── 4. Router conversacional ───────────────────────────────────────
            decision = await self.router.decide(turn)

            is_first_turn = turn.conversation_state.conversation_stage == ConversationStage.INICIO

            # ── 5+6. Parser + Search / KB (según la ruta) ─────────────────────
            search_result: SearchResult | None = None
            item_detail: dict | None = None
            kb_chunks: list[dict] = []

            if decision.actions.run_search:
                is_refinement = decision.route == Route.REFINAR_BUSQUEDA
                filters = await self.query_parser.parse(
                    mensaje=request.mensaje,
                    state=turn.conversation_state,
                    is_refinement=is_refinement,
                )
                search_result = await self.search_engine.search(
                    id_empresa=tenant_config.id_empresa,
                    id_rubro=tenant_config.id_rubro,
                    filters=filters,
                    limit=settings.MAX_ITEMS_PER_RESPONSE,
                )
            elif decision.route == Route.VER_DETALLE_ITEM:
                item_ref = (
                    decision.entities.get("item_referenciado")
                    or turn.conversation_state.ultimo_item_referenciado
                )
                if item_ref:
                    item_detail = await self.search_engine.get_item_detail(
                        id_empresa=tenant_config.id_empresa,
                        id_item=item_ref,
                    )
            elif decision.route == Route.PREGUNTA_KB:
                kb_chunks = await self.kb_service.search(
                    id_empresa=tenant_config.id_empresa,
                    id_rubro=tenant_config.id_rubro,
                    query=request.mensaje,
                )

            # ── 7. Actualizar estado ───────────────────────────────────────────
            new_state = self._advance_state(
                state=turn.conversation_state,
                decision=decision,
                search_result=search_result,
                filters=filters if decision.actions.run_search else None,
            )

            # ── 8. Construir respuesta (Sonnet → fallback plantilla) ────────────
            items_para_respuesta = search_result.items if search_result else []
            respuesta, ai_meta = await self._build_ai_response(
                decision=decision,
                turn=turn,
                cfg=tenant_config,
                state=new_state,
                is_first_turn=is_first_turn,
                search_result=search_result,
                item_detail=item_detail,
                kb_chunks=kb_chunks,
            )

            # ── 8b. Inyección determinística de fotos ──────────────────────────
            # Las fotos se inyectan FUERA del AI para garantizar que siempre
            # aparezcan todas, sin depender del comportamiento no determinístico
            # del modelo de lenguaje.
            if decision.route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA):
                respuesta = self._inject_fotos(respuesta, items_para_respuesta)

            # ── 9. Persistir mensaje del bot ───────────────────────────────────
            await self.context_manager.save_bot_message(
                id_conversacion=turn.id_conversacion,
                mensaje=respuesta,
            )

            # ── 10. Actualizar contexto ────────────────────────────────────────
            resumen = self._build_summary(new_state, request.mensaje, decision, search_result)
            await self.context_manager.update_context(
                id_conversacion=turn.id_conversacion,
                state=new_state,
                resumen=resumen,
            )

            # Calcular elapsed_ms antes de leads/analytics para que no infle el KPI
            elapsed_ms = int((time.monotonic() - start_ms) * 1000)

            # ── 11. Captura de lead ────────────────────────────────────────────
            id_lead_capturado: int | None = None
            if decision.actions.create_or_update_lead:
                id_lead_capturado = await self._capture_lead(
                    decision=decision,
                    request=request,
                    tenant_config=tenant_config,
                    id_conversacion=turn.id_conversacion,
                )

            # ── 12. Analytics (turno + evento de conversión) ───────────────────
            items_ids = [it.id_item for it in items_para_respuesta]
            await self._log_analytics(
                decision=decision,
                request=request,
                tenant_config=tenant_config,
                id_conversacion=turn.id_conversacion,
                ai_meta=ai_meta,
                items_ids=items_ids,
                elapsed_ms=elapsed_ms,
                id_lead=id_lead_capturado,
            )

            logger.info(
                "turn_completed",
                session_id=request.session_id,
                empresa=request.empresa_slug,
                route=decision.route.value,
                intent=decision.intent,
                confidence=round(decision.confidence, 2),
                used_ai_fallback=decision.used_ai_fallback,
                sonnet_used=not ai_meta.get("sonnet_fallback", True),
                stage=new_state.conversation_stage.value,
                items_devueltos=len(items_para_respuesta),
                lead_capturado=id_lead_capturado is not None,
                response_time_ms=elapsed_ms,
            )

            return ChatMessageResponse(
                session_id=request.session_id,
                conversation_id=turn.id_conversacion,
                respuesta=respuesta,
                items=[self._item_to_brief(it) for it in items_para_respuesta],
                route=decision.route.value,
                stage=new_state.conversation_stage.value,
                lead_capturado=new_state.lead_capturado,
                metadata={
                    "response_time_ms": elapsed_ms,
                    "fase": "6b",
                    "intent": decision.intent,
                    "confidence": round(decision.confidence, 2),
                    "used_ai_fallback": decision.used_ai_fallback,
                    "business_signals": decision.business_signals,
                    "total_encontrados": (
                        search_result.total_encontrados if search_result else None
                    ),
                    "id_lead": id_lead_capturado,
                    **ai_meta,
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

    # ─── Construcción de respuesta con IA ────────────────────────────────────

    async def _build_ai_response(
        self,
        decision,
        turn,
        cfg: TenantConfig,
        state,
        is_first_turn: bool,
        search_result,
        item_detail,
        kb_chunks: list[dict] | None = None,
    ) -> tuple[str, dict]:
        """
        Intenta redactar la respuesta con Sonnet vía PromptService + AIService.
        Si ia_habilitada=False o Sonnet falla, usa la plantilla determinística.

        Devuelve (texto_respuesta, ai_metadata).

        ai_metadata incluye:
          - sonnet_fallback: bool   — True si se usó plantilla
          - sonnet_reason: str      — motivo del fallback (si aplica)
          - sonnet_tokens_in: int   — tokens consumidos (si éxito)
          - sonnet_tokens_out: int
          - sonnet_ms: int          — latencia Sonnet (si éxito)
          - kb_chunks_used: int     — chunks KB inyectados al prompt (si ruta KB)
          - kb_fallback: bool       — True si KB no encontró contenido
        """
        chunks = kb_chunks or []

        # Rama: IA deshabilitada para este tenant
        if not cfg.ia_habilitada:
            respuesta = self._build_response(
                decision=decision, turn=turn, cfg=cfg, state=state,
                is_first_turn=is_first_turn, search_result=search_result,
                item_detail=item_detail, kb_chunks=chunks,
            )
            return respuesta, {"sonnet_fallback": True, "sonnet_reason": "ia_disabled"}

        # Rama: IA habilitada → intentar Sonnet
        try:
            system_prompt, messages = self.prompt_service.build_prompt(
                route=decision.route,
                turn=turn,
                cfg=cfg,
                search_result=search_result,
                item_detail=item_detail,
                is_first_turn=is_first_turn,
                kb_chunks=chunks,
            )
            ai_result = await self.ai_service.generate_response(
                system_prompt=system_prompt,
                messages=messages,
            )
        except Exception as exc:
            logger.error(
                "ai_response_build_failed",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            ai_result = {"used_fallback": True}

        if ai_result.get("used_fallback") or not ai_result.get("text"):
            # Fallback: plantilla determinística
            respuesta = self._build_response(
                decision=decision, turn=turn, cfg=cfg, state=state,
                is_first_turn=is_first_turn, search_result=search_result,
                item_detail=item_detail, kb_chunks=chunks,
            )
            return respuesta, {
                "sonnet_fallback": True,
                "sonnet_reason": "sonnet_error",
                "kb_chunks_used": len(chunks),
                "kb_fallback": len(chunks) == 0,
            }

        return ai_result["text"], {
            "sonnet_fallback": False,
            "sonnet_tokens_in": ai_result["tokens_input"],
            "sonnet_tokens_out": ai_result["tokens_output"],
            "sonnet_ms": ai_result["response_time_ms"],
            "kb_chunks_used": len(chunks),
            "kb_fallback": len(chunks) == 0,
        }

    # ─── Captura de lead ──────────────────────────────────────────────────────

    async def _capture_lead(
        self,
        decision: RouterDecision,
        request,
        tenant_config: TenantConfig,
        id_conversacion: int | None,
    ) -> int | None:
        """
        Crea un lead a partir de la señal comercial detectada por el router.
        Extrae nombre, teléfono y email del mensaje cuando sea posible.
        Vincula la conversación con el lead creado.

        Devuelve id_lead si se creó correctamente, None si hubo error.
        """
        try:
            raw_text = decision.entities.get("datos_contacto", request.mensaje)
            nombre, telefono, email = _parse_contact_data(raw_text)

            lead_response = await self.leads_service.create_from_conversation(
                id_empresa=tenant_config.id_empresa,
                canal=request.canal,
                nombre=nombre,
                telefono=telefono,
                email=email,
                metadata={
                    "session_id": request.session_id,
                    "route": decision.route.value,
                    "intent": decision.intent,
                    "mensaje_original": raw_text[:200],
                },
            )

            # Vincular conversación ↔ lead
            if id_conversacion:
                await self.context_manager.link_lead(
                    id_conversacion=id_conversacion,
                    id_lead=lead_response.id_lead,
                )

            logger.info(
                "lead_captured",
                id_lead=lead_response.id_lead,
                id_conversacion=id_conversacion,
                tiene_telefono=telefono is not None,
                tiene_email=email is not None,
            )
            return lead_response.id_lead

        except Exception as exc:
            logger.warning(
                "lead_capture_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                session_id=request.session_id,
            )
            return None

    # ─── Analytics ────────────────────────────────────────────────────────────

    async def _log_analytics(
        self,
        decision: RouterDecision,
        request,
        tenant_config: TenantConfig,
        id_conversacion: int | None,
        ai_meta: dict,
        items_ids: list[str],
        elapsed_ms: int,
        id_lead: int | None,
    ) -> None:
        """
        Registra el turno en premium_chat_logs y, si corresponde, el evento
        de conversión en premium_conversion_logs.

        Los errores en analytics nunca deben bloquear la respuesta al usuario.
        """
        # Determinar modelo y tokens usados
        if ai_meta.get("sonnet_fallback"):
            model_usado = "deterministic"
            tokens_input = 0
            tokens_output = 0
        else:
            model_usado = settings.SONNET_MODEL
            tokens_input = ai_meta.get("sonnet_tokens_in", 0)
            tokens_output = ai_meta.get("sonnet_tokens_out", 0)

        try:
            await self.analytics_service.log_chat_turn(
                id_empresa=tenant_config.id_empresa,
                id_rubro=tenant_config.id_rubro,
                id_conversacion=id_conversacion,
                id_lead=id_lead,
                session_id=request.session_id,
                canal=request.canal,
                consulta=request.mensaje,
                decision=decision,
                model_usado=model_usado,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                response_time_ms=elapsed_ms,
                items_ids=items_ids,
            )
        except Exception as exc:
            logger.warning(
                "analytics_chat_log_failed",
                error=str(exc),
                session_id=request.session_id,
            )

        # Evento de conversión (si el router lo marcó)
        if decision.actions.register_conversion_event and decision.actions.conversion_event:
            try:
                await self.analytics_service.log_conversion_event(
                    id_empresa=tenant_config.id_empresa,
                    id_rubro=tenant_config.id_rubro,
                    canal=request.canal,
                    evento=decision.actions.conversion_event,
                    id_conversacion=id_conversacion,
                    id_lead=id_lead,
                    session_id=request.session_id,
                    items_ids=items_ids or None,
                    metadata={
                        "intent": decision.intent,
                        "route": decision.route.value,
                    },
                )
            except Exception as exc:
                logger.warning(
                    "analytics_conversion_log_failed",
                    error=str(exc),
                    evento=decision.actions.conversion_event.value
                    if decision.actions.conversion_event
                    else None,
                )

    # ─── Estado conversacional ────────────────────────────────────────────────

    def _advance_state(
        self,
        state: ConversationState,
        decision: RouterDecision,
        search_result: SearchResult | None,
        filters: SearchFilters | None,
    ) -> ConversationState:
        now_iso = datetime.now(timezone.utc).isoformat()
        state.last_user_message_at = now_iso
        state.intent_previa = state.route_actual
        state.route_actual = decision.route.value

        # Primer turno → exploración
        if state.conversation_stage == ConversationStage.INICIO:
            state.conversation_stage = ConversationStage.EXPLORACION

        route = decision.route

        # Actualizar filtros activos cuando hay búsqueda
        if filters and route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA):
            state.conversation_stage = ConversationStage.EXPLORACION
            state.filters_activos = {
                "tipo": filters.tipo,
                "categoria": filters.categoria,
                "zona": filters.zona,
                "precio_min": filters.precio_min,
                "precio_max": filters.precio_max,
                "moneda": filters.moneda,
                "atributos": filters.atributos,
            }
            state.esperando_contacto = False
            state.esperando_visita = False

        # Actualizar items_recientes con los resultados
        if search_result and search_result.items:
            ids = [it.id_item for it in search_result.items]
            state.items_recientes = ids
            state.items_recientes_resumen = [
                ItemSummary(
                    id_item=it.id_item,
                    label=f"opcion_{i + 1}",
                    titulo=it.titulo,
                )
                for i, it in enumerate(search_result.items)
            ]
            state.ultimo_item_referenciado = ids[0]  # default: primer resultado

        # Ver detalle
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

        # Lead capturado
        if decision.intent == "datos_de_contacto_provistos":
            state.lead_capturado = True
            state.esperando_contacto = False
            state.esperando_visita = False

        return state

    # ─── Respuestas ───────────────────────────────────────────────────────────

    def _build_response(
        self,
        decision: RouterDecision,
        turn,
        cfg: TenantConfig,
        state: ConversationState,
        is_first_turn: bool,
        search_result: SearchResult | None,
        item_detail: dict | None,
        kb_chunks: list[dict] | None = None,
    ) -> str:
        route = decision.route
        nombre = cfg.nombre_empresa

        # ── Saludo ─────────────────────────────────────────────────────────────
        if route == Route.SALUDO:
            if is_first_turn:
                return (
                    f"¡Hola! Soy el asistente virtual de {nombre}. "
                    "Estoy acá para ayudarte a encontrar la propiedad ideal. "
                    "¿Qué tipo de propiedad estás buscando y en qué zona?"
                )
            return (
                "¡Hola de nuevo! ¿En qué puedo ayudarte hoy? "
                "Podés pedirme propiedades, filtrar por precio o zona, o consultar cualquier duda."
            )

        # ── Búsqueda / Refinamiento ────────────────────────────────────────────
        if route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA):
            intro = f"Hola, soy el asistente de {nombre}. " if is_first_turn else ""
            return self._build_search_response(intro, search_result, state)

        # ── Ver detalle ────────────────────────────────────────────────────────
        if route == Route.VER_DETALLE_ITEM:
            return self._build_detail_response(item_detail, state)

        # ── Contacto / Asesor ──────────────────────────────────────────────────
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

        # ── Visita ─────────────────────────────────────────────────────────────
        if route == Route.AGENDAR_VISITA:
            if decision.intent == "datos_de_contacto_provistos":
                return (
                    "¡Perfecto! Ya recibimos tus datos. "
                    f"Un asesor de {nombre} se va a comunicar con vos para confirmar la visita. "
                    "¿Hay algo más en lo que pueda ayudarte?"
                )
            prop_ref = ""
            if state.ultimo_item_referenciado:
                for it in state.items_recientes_resumen:
                    if it.id_item == state.ultimo_item_referenciado:
                        prop_ref = f' a "{it.titulo}"'
                        break
            return (
                f"¡Genial que quieras conocer{prop_ref} en persona! "
                "Para coordinar la visita necesito tu nombre y número de contacto."
            )

        # ── KB ─────────────────────────────────────────────────────────────────
        if route == Route.PREGUNTA_KB:
            if kb_chunks:
                # Hay contenido: extraer el primer chunk como respuesta base
                primer_chunk = kb_chunks[0].get("chunk_texto", "")
                return (
                    f"{primer_chunk[:500]}\n\n"
                    f"¿Necesitás más información? Podés consultarnos directamente en {nombre}."
                )
            return (
                f"No encontré información específica sobre eso en nuestra base de datos. "
                f"Te recomiendo contactar directamente a {nombre} para que un asesor pueda ayudarte."
            )

        # ── Fallback ───────────────────────────────────────────────────────────
        return (
            "Entendido. ¿Podés contarme un poco más sobre lo que estás buscando? "
            "Así puedo ayudarte mejor."
        )

    def _build_search_response(
        self,
        intro: str,
        search_result: SearchResult | None,
        state: ConversationState,
    ) -> str:
        if not search_result or search_result.total_encontrados == 0:
            filtros_str = self._filtros_activos_str(state.filters_activos)
            return (
                f"{intro}No encontré propiedades con esos criterios"
                f"{(' (' + filtros_str + ')') if filtros_str else ''}. "
                "¿Querés que busque con filtros menos restrictivos o cambiamos la zona?"
            )

        total = search_result.total_encontrados
        items = search_result.items
        n = len(items)

        # Intro de cantidad
        if total == 1:
            texto = f"{intro}Encontré 1 propiedad que coincide con tu búsqueda:\n\n"
        elif total <= n:
            texto = f"{intro}Encontré {total} propiedades para vos:\n\n"
        else:
            texto = f"{intro}Encontré {total} propiedades. Te muestro las mejores {n}:\n\n"

        # Listado de items
        for i, it in enumerate(items, 1):
            atrib = it.atributos or {}
            barrio = atrib.get("barrio") or atrib.get("ciudad") or ""
            dorms = atrib.get("dormitorios")
            ambientes = atrib.get("ambientes")

            linea = f"{i}. **{it.titulo}**"
            detalles = []
            if barrio:
                detalles.append(barrio)
            if ambientes:
                detalles.append(f"{ambientes} amb.")
            elif dorms:
                detalles.append(f"{dorms} dorm.")
            if it.precio and it.precio > 0:
                detalles.append(f"{it.moneda or 'USD'} {int(it.precio):,}".replace(",", "."))
            elif it.descripcion_corta:
                # Usar descripción corta si no hay precio
                detalles.append(it.descripcion_corta[:60])

            if detalles:
                linea += f" — {' | '.join(detalles)}"
            texto += linea + "\n"

        texto += "\n¿Querés ver más detalles de alguna de estas propiedades o ajustar la búsqueda?"
        return texto

    def _build_detail_response(
        self,
        item_detail: dict | None,
        state: ConversationState,
    ) -> str:
        if not item_detail:
            return (
                "No pude encontrar esa propiedad. "
                "¿Podés indicarme cuál te interesa? "
                "(Por ejemplo: 'el primero', 'el segundo', etc.)"
            )

        atrib = item_detail.get("atributos") or {}
        if isinstance(atrib, str):
            import json
            atrib = json.loads(atrib)

        barrio = atrib.get("barrio") or atrib.get("ciudad") or ""
        calle = atrib.get("calle") or ""
        dorms = atrib.get("dormitorios")
        banios = atrib.get("banios")
        ambientes = atrib.get("ambientes")
        sup_total = atrib.get("superficie_total")
        sup_cub = atrib.get("superficie_cubierta")
        detalles_arr = atrib.get("detalles") or []
        estado = atrib.get("estado_construccion")

        precio = item_detail.get("precio")
        moneda = item_detail.get("moneda") or "USD"

        lineas = [f"**{item_detail['titulo']}**\n"]

        # Ubicación
        if calle or barrio:
            lineas.append(f"📍 {', '.join(filter(None, [calle, barrio]))}")

        # Características
        caract = []
        if ambientes:
            caract.append(f"{ambientes} ambientes")
        elif dorms:
            caract.append(f"{dorms} dormitorios")
        if banios:
            caract.append(f"{banios} baños")
        if sup_cub:
            caract.append(f"{sup_cub} cubiertos")
        elif sup_total:
            caract.append(f"{sup_total} totales")
        if caract:
            lineas.append("🏠 " + " | ".join(caract))

        # Precio
        if precio and precio > 0:
            lineas.append(f"💰 {moneda} {int(precio):,}".replace(",", "."))

        # Detalles / amenities
        if detalles_arr:
            lineas.append(f"✅ {', '.join(detalles_arr).capitalize()}")

        # Estado
        if estado:
            lineas.append(f"🔑 Estado: {estado.replace('_', ' ')}")

        # Descripción corta
        desc = item_detail.get("descripcion_corta") or item_detail.get("descripcion")
        if desc:
            lineas.append(f"\n{desc[:200]}")

        lineas.append("\n¿Te interesa coordinar una visita o hablar con un asesor?")

        return "\n".join(lineas)

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _filtros_activos_str(self, filters_activos: dict) -> str:
        parts = []
        if filters_activos.get("tipo"):
            parts.append(filters_activos["tipo"])
        if filters_activos.get("zona"):
            parts.append(f"en {filters_activos['zona']}")
        if filters_activos.get("precio_max"):
            m = filters_activos.get("moneda", "USD")
            parts.append(f"hasta {m} {int(filters_activos['precio_max']):,}".replace(",", "."))
        return ", ".join(parts)

    def _inject_fotos(self, respuesta: str, items: list[ItemCandidate]) -> str:
        """
        Inyecta las URLs de fotos de cada propiedad en la respuesta de forma
        determinística, independientemente de lo que haya incluido el AI.

        Estrategia:
          - Para cada item con fotos, busca "N." al inicio de línea (el número
            de la propiedad en la lista) y agrega las URLs justo antes del
            siguiente item o al final si es el último.
          - Si la primera URL ya está en el texto, omite ese item (el AI ya
            la incluyó correctamente).
        """
        if not items or not any(it.fotos for it in items):
            return respuesta

        for idx, item in enumerate(items):
            if not item.fotos:
                continue
            # Si el AI ya incluyó la primera foto, asumir que incluyó todas
            if item.fotos[0] in respuesta:
                continue

            num = idx + 1
            fotos_block = "\n".join(item.fotos[:3])

            if idx + 1 < len(items):
                # Insertar antes del siguiente número de propiedad
                siguiente = idx + 2
                pattern = re.compile(rf"(?m)^({siguiente}\.)", re.MULTILINE)
                if pattern.search(respuesta):
                    respuesta = pattern.sub(
                        fotos_block + r"\n\n\1", respuesta, count=1
                    )
                    continue
            # Última propiedad o no encontró el siguiente número: agregar al final
            respuesta = respuesta.rstrip() + "\n\n" + fotos_block

        return respuesta

    def _item_to_brief(self, item: ItemCandidate) -> ItemBrief:
        atrib = item.atributos or {}
        return ItemBrief(
            id_item=item.id_item,
            titulo=item.titulo,
            tipo=item.tipo,
            categoria=item.categoria,
            precio=item.precio,
            moneda=item.moneda,
            descripcion_corta=item.descripcion_corta,
            fotos=item.fotos[:3],  # máximo 3 fotos en la respuesta
            atributos=atrib,
        )

    def _build_summary(
        self,
        state: ConversationState,
        mensaje: str,
        decision: RouterDecision,
        search_result: SearchResult | None,
    ) -> str | None:
        if state.conversation_stage == ConversationStage.INICIO:
            return None

        stage_label = {
            ConversationStage.EXPLORACION: "explorando propiedades",
            ConversationStage.INTERES: "con interés en una propiedad específica",
            ConversationStage.CONVERSION: "en proceso de conversión (contacto/visita)",
            ConversationStage.CERRADA: "conversación cerrada",
        }.get(state.conversation_stage, "")

        filtros = state.filters_activos
        filtros_str = (
            f" Filtros: {self._filtros_activos_str(filtros)}."
            if filtros and any(filtros.values())
            else ""
        )

        resultados_str = ""
        if search_result:
            resultados_str = f" Encontrados: {search_result.total_encontrados}."

        signals_str = ""
        if state.advisor_requested:
            signals_str += " Solicitó asesor."
        if state.visit_requested:
            signals_str += " Solicitó visita."
        if state.lead_capturado:
            signals_str += " Lead capturado."

        return (
            f"El usuario está {stage_label}. "
            f"Ruta: {decision.route.value} (intent: {decision.intent}). "
            f'Último mensaje: "{mensaje[:120]}".{filtros_str}{resultados_str}{signals_str}'
        )
