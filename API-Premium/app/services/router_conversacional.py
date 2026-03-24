"""
RouterConversacional — decide la ruta operativa de cada turno.

Responsabilidades:
- Clasificar la intención del mensaje usando reglas determinísticas
- Usar el contexto conversacional para resolver referencias y refinamientos
- Invocar Haiku solo como fallback cuando las reglas no son suficientes
- Devolver una RouterDecision con acciones explícitas y business_signals

Prioridad de rutas (de mayor a menor):
  1. agendar_visita
  2. contactar_asesor
  3. ver_detalle_item       (solo si hay items_recientes)
  4. refinar_busqueda       (solo si hay búsqueda activa)
  5. buscar_catalogo
  6. pregunta_kb
  7. saludo
  8. fallback (+ Haiku si las reglas no alcanzan)

No debe:
- Parsear filtros detallados (eso es del QueryParser)
- Ejecutar búsquedas SQL
- Redactar respuestas finales
"""
import re

from app.core.logging import get_logger
from app.models.domain_models import (
    ConversionEvent,
    ConversationStage,
    ConversationState,
    Route,
    RouterActions,
    RouterDecision,
    TurnContext,
)
from app.services.ai_service import AIService

logger = get_logger(__name__)

# ─── Patrones compilados ───────────────────────────────────────────────────────

_PAT_VISITA = re.compile(
    r"\b("
    r"quiero\s+(visitar(la)?|ver\s+en\s+persona|conocer(la)?|verla)|"
    r"puedo\s+(visitar|ver|ir\s+a\s+verla?)|"
    r"coordinar\s+(?:la\s+|una\s+)?visita|"
    r"sacar\s+turno|"
    r"cuando\s+puedo\s+(ir|verla?|visitarla?)|"
    r"me\s+gustar[ií]a\s+(ir|verla?|visitarla?)|"
    r"posibilidad\s+de\s+(visitar|ver\s+la)|"
    r"quiero\s+(?:conocer|ver)\s+(?:el|la|un[ao]?)\s+(?:departamento|casa|lote|campo|propiedad|inmueble)"
    r")\b",
    re.IGNORECASE,
)

_PAT_ASESOR = re.compile(
    r"\b("
    r"hablar\s+con\s+(un\s+)?asesor|"
    r"quiero\s+que\s+me\s+llamen|"
    r"me\s+pueden?\s+llamar|"
    r"me\s+llamen|"
    r"contactar\s+(un\s+)?asesor|"
    r"hablar\s+con\s+alguien|"
    r"me\s+interesa\s+hablar|"
    r"pueden?\s+contactarme|"
    r"comunic[aá]rme\s+con|"
    r"escribirme"
    r")\b",
    re.IGNORECASE,
)

_PAT_SALUDO = re.compile(
    r"^[\s¡!]*("
    r"hola|buenos?\s+d[ií]as?|buenas\s+tardes?|buenas\s+noches?|"
    r"buenas|hi|hello|saludos|hey|qu[eé]\s+tal|"
    r"c[oó]mo\s+est[aá]s?|buen\s+d[ií]a"
    r")[\s!¡.]*$",
    re.IGNORECASE,
)

_PAT_BUSQUEDA = re.compile(
    r"\b("
    r"busco|buscar|"
    r"quiero\s+(comprar|alquilar|ver|un[ao]?|encontrar)|"
    r"necesito\s+(un[ao]?\s+)?|"
    r"ten[eé]s?|tienen|"
    r"hay\s+(algún?|casas?|departamentos?|lotes?|campos?|alguna?)|"
    r"mostrame|mu[eé]strame|"
    r"propiedades?\s+(en\s+)?(venta|alquiler)|"
    r"\b(casas?|departamentos?|deptos?|lotes?|campos?|terrenos?|ph\b|cocheras?)\b"
    r")",
    re.IGNORECASE,
)

_PAT_REFINAMIENTO = re.compile(
    r"\b("
    r"m[aá]s\s+(barato|econ[oó]mico|accesible|caro|grande|chico|peque[nñ]o|amplio)|"
    r"algo\s+m[aá]s\s+(barato|econ[oó]mico|caro|grande|chico)|"
    r"con\s+(balc[oó]n|pileta|cochera|garage|patio|jard[ií]n|amenities|parrilla|laundry)|"
    r"sin\s+(expensas?|cochera|balc[oó]n)|"
    r"en\s+otra\s+zona|"
    r"otro\s+(barrio|sector|lado)|"
    r"de\s+[1-9]\s+ambientes?|"
    r"[1-9]\s+ambientes?|"
    r"menos\s+de\s+(\$|usd\s*)?\d|"
    r"hasta\s+(\$|usd\s*)?\d|"
    r"menor\s+precio|"
    r"cambiar?\s+(la\s+)?(zona|precio|filtro)|"
    r"filtrar?\s+por"
    r")\b",
    re.IGNORECASE,
)

_PAT_DETALLE = re.compile(
    r"\b("
    r"el\s+primero?|la\s+primera?|"
    r"el\s+segundo?|la\s+segunda?|"
    r"el\s+tercero?|la\s+tercera?|"
    r"opci[oó]n\s+[123]|la\s+opci[oó]n\s+[123]|"
    r"[123][°º]\s+opci[oó]n|"
    r"ese\s+(departamento|casa|lote|campo|inmueble|uno)?|"
    r"esa\s+(propiedad|opci[oó]n|casa)?|"
    r"m[aá]s\s+informaci[oó]n|"
    r"m[aá]s\s+detalles?|"
    r"m[aá]s\s+datos?|"
    r"m[aá]s\s+info|"
    r"cont[aá]me\s+m[aá]s|"
    r"quiero\s+saber\s+m[aá]s"
    r")\b",
    re.IGNORECASE,
)

_PAT_KB = re.compile(
    r"\b("
    r"c[oó]mo\s+funciona|"
    r"expensas?|"
    r"tr[aá]mites?|"
    r"documentaci[oó]n(\s+necesaria|\s+requerida)?|"
    r"cu[aá]nto\s+tarda|"
    r"preguntas?\s+frecuentes?|"
    r"condiciones?\s+(de\s+)?(venta|alquiler)|"
    r"qu[eé]\s+incluye|"
    r"qu[eé]\s+tengo\s+que\s+(hacer|presentar)|"
    r"escritura|"
    r"hipoteca|"
    r"cr[eé]dito\s+hipotecario|"
    r"comisi[oó]n|"
    r"honorarios?|"
    r"tasaci[oó]n|"
    r"valuaci[oó]n|"
    r"proceso\s+de\s+(compra|venta|alquiler)|"
    r"formas?\s+de\s+pago|"
    r"horario|"
    r"cu[aá]ndo\s+atienden|"
    r"garantias?|"
    r"fianza|"
    r"dep[oó]sito\s+de\s+garantia|"
    r"seguro\s+de\s+cau[cç]i[oó]n|"
    r"pasos?\s+para"
    r")\b",
    re.IGNORECASE,
)

# Datos de contacto: nombre completo o teléfono
_PAT_CONTACTO_DATOS = re.compile(
    r"(\d{6,}|[A-ZÁÉÍÓÚ][a-záéíóú]{1,}\s+[A-ZÁÉÍÓÚ][a-záéíóú]{1,})",
)

# Ordinales para resolución de items
_ORDINALES = [
    [r"\bprimero?\b", r"\bprimera?\b", r"\bopci[oó]n\s+1\b", r"\b1[°º]\b"],
    [r"\bsegundo?\b", r"\bsegunda?\b", r"\bopci[oó]n\s+2\b", r"\b2[°º]\b"],
    [r"\btercero?\b", r"\btercera?\b", r"\bopci[oó]n\s+3\b", r"\b3[°º]\b"],
]

_CANDIDATE_ROUTES = [
    Route.SALUDO,
    Route.BUSCAR_CATALOGO,
    Route.REFINAR_BUSQUEDA,
    Route.VER_DETALLE_ITEM,
    Route.CONTACTAR_ASESOR,
    Route.AGENDAR_VISITA,
    Route.PREGUNTA_KB,
    Route.FALLBACK,
]


class RouterConversacional:
    def __init__(self) -> None:
        self.ai_service = AIService()

    async def decide(self, turn: TurnContext) -> RouterDecision:
        """
        Decide la ruta operativa para el turno actual.
        Primero aplica reglas determinísticas, luego Haiku como fallback.
        """
        decision = self._apply_rules(turn.mensaje, turn.conversation_state)

        if decision is not None:
            logger.debug(
                "router_decision_by_rules",
                route=decision.route.value,
                intent=decision.intent,
                confidence=decision.confidence,
            )
            return decision

        logger.debug("router_rules_inconclusive_using_haiku", mensaje_len=len(turn.mensaje))
        return await self._classify_with_haiku(turn.mensaje, turn.conversation_state)

    # ─── Reglas determinísticas ───────────────────────────────────────────────

    def _apply_rules(self, mensaje: str, state: ConversationState) -> RouterDecision | None:
        """
        Aplica reglas determinísticas sobre el mensaje y el estado.
        Devuelve None si las reglas no logran clasificar con suficiente confianza.
        """
        msg = mensaje.strip()

        # ── 1. Bot esperando datos de contacto: capturar si los provee ────────
        if (state.esperando_contacto or state.esperando_visita) and _PAT_CONTACTO_DATOS.search(msg):
            route = Route.AGENDAR_VISITA if state.esperando_visita else Route.CONTACTAR_ASESOR
            return RouterDecision(
                route=route,
                intent="datos_de_contacto_provistos",
                confidence=0.9,
                used_ai_fallback=False,
                entities={"datos_contacto": msg},
                actions=RouterActions(
                    run_ai_response=True,
                    create_or_update_lead=True,
                    register_conversion_event=True,
                    conversion_event=ConversionEvent.LEAD_CREATED,
                ),
                business_signals={"lead_signal": True},
            )

        # ── 3. Visita (alta prioridad comercial) ──────────────────────────────
        if _PAT_VISITA.search(msg):
            return RouterDecision(
                route=Route.AGENDAR_VISITA,
                intent="quiere_visitar",
                confidence=0.95,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(
                    run_ai_response=True,
                    register_conversion_event=True,
                    conversion_event=ConversionEvent.VISITA_REQUESTED,
                ),
                business_signals={"visit_intent": True},
            )

        # ── 4. Contacto / Asesor ──────────────────────────────────────────────
        if _PAT_ASESOR.search(msg):
            return RouterDecision(
                route=Route.CONTACTAR_ASESOR,
                intent="quiere_asesor",
                confidence=0.95,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(
                    run_ai_response=True,
                    register_conversion_event=True,
                    conversion_event=ConversionEvent.ASESOR_REQUESTED,
                ),
                business_signals={"asesor_intent": True},
            )

        # ── 5. Detalle de item (solo si hay items mostrados) ──────────────────
        if state.items_recientes and _PAT_DETALLE.search(msg):
            item_ref = self._resolve_item_reference(msg, state)
            return RouterDecision(
                route=Route.VER_DETALLE_ITEM,
                intent="ver_detalle_item",
                confidence=0.9,
                used_ai_fallback=False,
                entities={"item_referenciado": item_ref},
                actions=RouterActions(
                    run_ai_response=True,
                    register_conversion_event=True,
                    conversion_event=ConversionEvent.ITEM_DETAIL_VIEWED,
                ),
                business_signals={},
            )

        # ── 6. Refinamiento (solo si hay búsqueda activa) ─────────────────────
        if self._resolve_refinement(msg, state):
            return RouterDecision(
                route=Route.REFINAR_BUSQUEDA,
                intent="refinar_busqueda_activa",
                confidence=0.85,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(
                    run_parser=True,
                    run_search=True,
                    run_ai_response=True,
                ),
                business_signals={},
            )

        # ── 7. Pregunta informacional / KB (antes de búsqueda para tomar prioridad) ──
        if _PAT_KB.search(msg):
            return RouterDecision(
                route=Route.PREGUNTA_KB,
                intent="pregunta_informacional",
                confidence=0.8,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(
                    run_kb_search=True,
                    run_ai_response=True,
                ),
                business_signals={},
            )

        # ── 8. Nueva búsqueda en catálogo ─────────────────────────────────────
        if _PAT_BUSQUEDA.search(msg):
            return RouterDecision(
                route=Route.BUSCAR_CATALOGO,
                intent="busqueda_nueva",
                confidence=0.85,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(
                    run_parser=True,
                    run_search=True,
                    run_ai_response=True,
                ),
                business_signals={},
            )

        # ── 9. Saludo simple ──────────────────────────────────────────────────
        if _PAT_SALUDO.search(msg):
            return RouterDecision(
                route=Route.SALUDO,
                intent="saludo",
                confidence=0.9,
                used_ai_fallback=False,
                entities={},
                actions=RouterActions(run_ai_response=True),
                business_signals={},
            )

        # ── 10. Reglas insuficientes → delegar a Haiku ─────────────────────────
        return None

    # ─── Haiku fallback ───────────────────────────────────────────────────────

    async def _classify_with_haiku(
        self, mensaje: str, state: ConversationState
    ) -> RouterDecision:
        """
        Fallback: usa Haiku para clasificar la intención cuando las reglas no alcanzan.
        Solo se invoca si _apply_rules devuelve None.
        """
        result = await self.ai_service.classify_intent(mensaje, state, _CANDIDATE_ROUTES)

        route = result["route"]
        entities = result.get("entities", {})

        # Actions por ruta
        actions = RouterActions(run_ai_response=True)
        if route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA):
            actions.run_parser = True
            actions.run_search = True
        elif route == Route.VER_DETALLE_ITEM:
            # Haiku no resuelve ordinales — intentar con las reglas determinísticas
            if not entities.get("item_referenciado"):
                entities["item_referenciado"] = self._resolve_item_reference(mensaje, state)
            actions.register_conversion_event = True
            actions.conversion_event = ConversionEvent.ITEM_DETAIL_VIEWED
        elif route == Route.PREGUNTA_KB:
            actions.run_kb_search = True
        elif route == Route.CONTACTAR_ASESOR:
            actions.register_conversion_event = True
            actions.conversion_event = ConversionEvent.ASESOR_REQUESTED
            # Si el mensaje ya incluye datos de contacto → capturar lead de inmediato
            if _PAT_CONTACTO_DATOS.search(mensaje):
                actions.create_or_update_lead = True
                actions.conversion_event = ConversionEvent.LEAD_CREATED
        elif route == Route.AGENDAR_VISITA:
            actions.register_conversion_event = True
            actions.conversion_event = ConversionEvent.VISITA_REQUESTED
            if _PAT_CONTACTO_DATOS.search(mensaje):
                actions.create_or_update_lead = True

        logger.info(
            "router_decision_by_haiku",
            route=route.value,
            intent=result["intent"],
            confidence=result["confidence"],
        )

        return RouterDecision(
            route=route,
            intent=result["intent"],
            confidence=result["confidence"],
            used_ai_fallback=True,
            entities=entities,
            actions=actions,
            business_signals={},
        )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _resolve_refinement(self, mensaje: str, state: ConversationState) -> bool:
        """
        Detecta si el mensaje es un refinamiento de búsqueda previa.
        Aplica cuando hay filters/items activos O cuando la ruta previa fue una búsqueda
        (el SearchEngine puede no haberse ejecutado aún en fases tempranas).
        """
        _SEARCH_ROUTES = {"buscar_catalogo", "refinar_busqueda"}
        has_active_search = (
            bool(state.filters_activos)
            or bool(state.items_recientes)
            or state.route_actual in _SEARCH_ROUTES
        )
        if not has_active_search:
            return False
        return bool(_PAT_REFINAMIENTO.search(mensaje))

    def _resolve_item_reference(self, mensaje: str, state: ConversationState) -> str | None:
        """
        Resuelve referencias a items previos ("el primero", "ese", "la opción 2").
        Devuelve el id_item referenciado o None.
        """
        resumen = state.items_recientes_resumen
        if not resumen:
            return state.ultimo_item_referenciado

        msg = mensaje.lower()

        # Ordinales explícitos
        for idx, patterns in enumerate(_ORDINALES):
            if idx < len(resumen):
                if any(re.search(p, msg, re.IGNORECASE) for p in patterns):
                    return resumen[idx].id_item

        # Demostrativos ("ese", "esa", "eso") → último mostrado
        if re.search(r"\bese\b|\besa\b|\beso\b", msg):
            return state.ultimo_item_referenciado or (
                resumen[-1].id_item if resumen else None
            )

        return None