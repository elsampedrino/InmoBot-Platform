"""
PromptService — construcción dinámica del prompt final para Sonnet.

Responsabilidades:
- Ensamblar system_prompt: base del rubro + estilo + voz de marca + prompt extra
- Inyectar contexto conversacional (resumen en system, historial en messages)
- Inyectar datos estructurados según la ruta (items, item_detail)
- Devolver (system_prompt, messages) listos para AIService.generate_response()

Principio:
  La IA recibe datos ya buscados y procesados — solo redacta la respuesta.
  No decide rutas, no consulta catálogo, no genera filtros.

Rutas con bloque específico:
  saludo, buscar_catalogo, refinar_busqueda, ver_detalle_item,
  contactar_asesor, agendar_visita, pregunta_kb, fallback
"""
import json as _json

from app.core.logging import get_logger
from app.models.domain_models import (
    ConversationState,
    ItemCandidate,
    Route,
    SearchResult,
    TenantConfig,
    TurnContext,
)

logger = get_logger(__name__)

# ─── REGLAS OPERATIVAS BASE ───────────────────────────────────────────────────
# Se inyectan en todos los prompts para garantizar comportamiento consistente.
_REGLAS_BASE = """## REGLAS OPERATIVAS
- Respondé siempre en español con voseo rioplatense (Argentina).
- Sé conciso y natural. Preferí párrafos fluidos a listas largas cuando aplique.
- No inventes precios, disponibilidades ni características que no estén en los datos provistos.
- No repitas información que el usuario ya conoce (está en el historial de conversación).
- Usá los datos exactos que se te proveen. No infirás valores no presentes.
- Si no tenés información suficiente para responder algo, decilo honestamente.
- No uses emojis en exceso. Máximo 1-2 si el estilo de la empresa lo permite.
- No uses separadores horizontales (---) en ningún momento.""".strip()


class PromptService:

    def build_prompt(
        self,
        route: Route,
        turn: TurnContext,
        cfg: TenantConfig,
        search_result: SearchResult | None,
        item_detail: dict | None,
        is_first_turn: bool,
        kb_chunks: list[dict] | None = None,
    ) -> tuple[str, list[dict]]:
        """
        Entry point principal.
        Construye y devuelve (system_prompt, messages) listos para AIService.

        system_prompt: configuración base + voz de marca + contexto conversacional
                       + bloque de tarea específico por ruta
        messages:      historial reciente (alternado user/assistant) + mensaje actual
        """
        base_system = self._build_base_system(cfg, turn.resumen_contexto)
        route_block = self._build_route_block(
            route=route,
            turn=turn,
            cfg=cfg,
            search_result=search_result,
            item_detail=item_detail,
            is_first_turn=is_first_turn,
            kb_chunks=kb_chunks or [],
        )
        system_prompt = base_system
        if route_block:
            system_prompt = base_system + "\n\n" + route_block

        messages = self._build_messages(turn)

        logger.debug(
            "prompt_built",
            route=route.value,
            system_len=len(system_prompt),
            messages_count=len(messages),
        )
        return system_prompt, messages

    # ─── Sistema base ──────────────────────────────────────────────────────────

    def _build_base_system(
        self, cfg: TenantConfig, resumen_contexto: str | None
    ) -> str:
        """
        Ensambla el bloque de sistema base en capas:
          1. system_prompt del rubro (rol del asistente)
          2. style_prompt (tono, formato)
          3. brand_voice de la empresa
          4. prompt_extra de la empresa (instrucciones específicas)
          5. Reglas operativas invariantes
          6. Resumen del contexto conversacional (si hay historial previo)
        """
        parts = [cfg.system_prompt]

        if cfg.style_prompt:
            parts.append(f"## ESTILO DE COMUNICACIÓN\n{cfg.style_prompt}")

        if cfg.brand_voice:
            parts.append(f"## VOZ DE MARCA\n{cfg.brand_voice}")

        if cfg.prompt_extra:
            parts.append(
                f"## INSTRUCCIONES ESPECÍFICAS DE {cfg.nombre_empresa.upper()}\n"
                f"{cfg.prompt_extra}"
            )

        parts.append(_REGLAS_BASE)

        if resumen_contexto:
            parts.append(
                f"## CONTEXTO DE LA CONVERSACIÓN HASTA AHORA\n{resumen_contexto}"
            )

        return "\n\n".join(parts)

    # ─── Bloques de tarea por ruta ─────────────────────────────────────────────

    def _build_route_block(
        self,
        route: Route,
        turn: TurnContext,
        cfg: TenantConfig,
        search_result: SearchResult | None,
        item_detail: dict | None,
        is_first_turn: bool,
        kb_chunks: list[dict] | None = None,
    ) -> str | None:
        """Despacha al bloque de tarea correspondiente a la ruta."""
        if route == Route.SALUDO:
            return self._block_saludo(cfg, is_first_turn)

        if route in (Route.BUSCAR_CATALOGO, Route.REFINAR_BUSQUEDA):
            return self._block_busqueda(
                search_result=search_result,
                state=turn.conversation_state,
                es_refinamiento=(route == Route.REFINAR_BUSQUEDA),
            )

        if route == Route.VER_DETALLE_ITEM:
            return self._block_detalle(item_detail)

        if route == Route.CONTACTAR_ASESOR:
            return self._block_contacto(cfg, turn.conversation_state)

        if route == Route.AGENDAR_VISITA:
            return self._block_visita(cfg, turn.conversation_state)

        if route == Route.PREGUNTA_KB:
            return self._block_kb(kb_chunks or [])

        if route == Route.FALLBACK:
            return self._block_fallback()

        return None

    # ─── Bloques específicos ───────────────────────────────────────────────────

    def _block_saludo(self, cfg: TenantConfig, is_first_turn: bool) -> str:
        if is_first_turn:
            return (
                "## TAREA\n"
                f"Es el primer mensaje del usuario con {cfg.nombre_empresa}.\n"
                f"Saludale de forma cálida y profesional. Presentate como el asistente virtual de {cfg.nombre_empresa}. "
                "En una o dos oraciones explicá que podés ayudarle a encontrar propiedades y preguntale "
                "qué tipo de propiedad busca y en qué zona."
            )
        return (
            "## TAREA\n"
            "El usuario está saludando en una conversación en curso. "
            "Respondé de forma breve y amable, y ofrecé continuar ayudándole con lo que necesite."
        )

    def _block_busqueda(
        self,
        search_result: SearchResult | None,
        state: ConversationState,
        es_refinamiento: bool,
    ) -> str:
        if not search_result or search_result.total_encontrados == 0:
            filtros = self._filtros_str(state.filters_activos)
            prefijo = "Luego del refinamiento, no" if es_refinamiento else "No"
            return (
                "## TAREA\n"
                f"{prefijo} se encontraron propiedades"
                f"{(' con los criterios: ' + filtros) if filtros else ''}.\n"
                "Informale al usuario con empatía. Sugerí alternativas concretas: "
                "ampliar criterios, cambiar zona, o consultar directamente con un asesor."
            )

        items = search_result.items
        items_text = self._format_items_for_prompt(items)

        instrucciones_comunes = (
            f"- Presentá TODAS las {len(items)} propiedades de la lista. No omitás ninguna.\n"
            f"- Numeralas del 1 al {len(items)} en el mismo orden en que aparecen arriba. No las reordenes.\n"
            "- Para cada una destacá lo más relevante: ubicación, dormitorios, precio (si tiene), algún detalle atractivo\n"
            "- No menciones cuántas propiedades hay en total ni cuántas quedan sin mostrar\n"
        )

        if es_refinamiento:
            return (
                "## TAREA\n"
                "Se aplicaron los nuevos criterios y estas son las propiedades que coinciden. "
                "Presentalas de forma natural y conversacional.\n\n"
                "## PROPIEDADES DISPONIBLES\n"
                f"{items_text}\n\n"
                "## INSTRUCCIONES\n"
                + instrucciones_comunes +
                "- No compares con las propiedades anteriores ni hagas conteos sobre ellas\n"
                "- Solo trabajá con los datos de las propiedades que se te proveen arriba\n"
                "- Al final invitá al usuario a pedir más detalles o a seguir refinando"
            )

        return (
            "## TAREA\n"
            "Estas son las opciones disponibles. Presentalas de forma natural y conversacional.\n\n"
            "## PROPIEDADES DISPONIBLES\n"
            f"{items_text}\n\n"
            "## INSTRUCCIONES\n"
            + instrucciones_comunes +
            "- Al final invitá al usuario a pedir más detalles de alguna o a refinar la búsqueda"
        )

    def _block_detalle(self, item_detail: dict | None) -> str:
        if not item_detail:
            return (
                "## TAREA\n"
                "No se encontró el detalle de la propiedad solicitada. "
                "Informalo con amabilidad y preguntá si puede indicarte cuál propiedad le interesa "
                "(por ejemplo: 'el primero', 'el segundo', o por su nombre)."
            )

        atrib = item_detail.get("atributos") or {}
        if isinstance(atrib, str):
            atrib = _json.loads(atrib)

        precio = item_detail.get("precio")
        moneda = item_detail.get("moneda", "USD")
        precio_str = (
            f"{moneda} {int(precio):,}".replace(",", ".")
            if precio and precio > 0
            else "A consultar"
        )
        detalles = atrib.get("detalles") or []
        detalles_str = ", ".join(detalles) if detalles else "No especificados"

        prop_data = (
            f"Título: {item_detail.get('titulo', '')}\n"
            f"Tipo: {item_detail.get('tipo', '')} | Operación: {item_detail.get('categoria', '')}\n"
            f"Dirección: {atrib.get('calle', '')} — {atrib.get('barrio', '') or atrib.get('ciudad', '')}\n"
            f"Dormitorios: {atrib.get('dormitorios', 'N/D')} | Baños: {atrib.get('banios', 'N/D')}\n"
            f"Sup. cubierta: {atrib.get('superficie_cubierta', 'N/D')} | Total: {atrib.get('superficie_total', 'N/D')}\n"
            f"Precio: {precio_str}\n"
            f"Amenities/Detalles: {detalles_str}\n"
            f"Estado: {atrib.get('estado_construccion', 'N/D')}\n"
            f"Descripción: {item_detail.get('descripcion') or item_detail.get('descripcion_corta', '')}"
        )

        return (
            "## TAREA\n"
            "Describí esta propiedad de forma atractiva y comercial para generar interés genuino.\n\n"
            "## DATOS DE LA PROPIEDAD\n"
            f"{prop_data}\n\n"
            "## INSTRUCCIONES\n"
            "- Usá ÚNICAMENTE los datos que se te proveen arriba. No uses información del historial de conversación.\n"
            "- Si el historial menciona otras propiedades o datos distintos, ignoralos por completo.\n"
            "- Organizá la información de forma natural, no como una lista de datos fríos\n"
            "- Destacá los puntos más atractivos para un comprador o inquilino\n"
            "- Mencioná ubicación, características físicas y amenities que sumen valor\n"
            "- Si tiene precio, presentalo claramente\n"
            "- Cerrá con una invitación concreta: coordinar visita o hablar con un asesor"
        )

    def _block_contacto(self, cfg: TenantConfig, state: ConversationState) -> str:
        prop_info = self._ultimo_item_titulo(state)
        prop_line = f"\nPropiedad de interés: {prop_info}" if prop_info else ""
        return (
            "## TAREA\n"
            f"El usuario quiere contactar con un asesor de {cfg.nombre_empresa}.{prop_line}\n"
            "Respondé con entusiasmo. Pedile amablemente su nombre y número de teléfono (o WhatsApp) "
            f"para que el equipo de {cfg.nombre_empresa} se contacte a la brevedad."
        )

    def _block_visita(self, cfg: TenantConfig, state: ConversationState) -> str:
        prop_info = self._ultimo_item_titulo(state)
        prop_line = f"\nPropiedad a visitar: {prop_info}" if prop_info else ""
        return (
            "## TAREA\n"
            f"El usuario quiere coordinar una visita presencial.{prop_line}\n"
            "Respondé con entusiasmo. Confirmá la propiedad si la conocés. "
            f"Pedile nombre y teléfono para que el equipo de {cfg.nombre_empresa} "
            "confirme fecha y horario."
        )

    def _block_kb(self, chunks: list[dict]) -> str:
        """
        Bloque de tarea para preguntas institucionales.

        Si hay chunks: inyecta el contenido como fuente de verdad.
        Si no hay chunks: instrucción explícita de no inventar información.

        Principio: Sonnet solo redacta, la KB es la fuente.
        """
        if not chunks:
            return (
                "## TAREA\n"
                "El usuario tiene una pregunta sobre la empresa o el proceso inmobiliario. "
                "No se encontró información específica en la base de conocimiento. "
                "Respondé con honestidad que no tenés esa información disponible en este momento "
                "y sugerí que contacte directamente con la inmobiliaria para obtener una respuesta precisa. "
                "No inventes ni supongas datos, precios ni condiciones."
            )

        # Formatear chunks como contexto numerado
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_titulo = chunk.get("doc_titulo", "Información general")
            texto = chunk.get("chunk_texto", "").strip()
            context_parts.append(f"[Fuente {i} — {doc_titulo}]\n{texto}")

        context_str = "\n\n".join(context_parts)

        return (
            "## TAREA\n"
            "El usuario tiene una pregunta sobre la empresa o el proceso inmobiliario. "
            "Respondé usando EXCLUSIVAMENTE la información de la base de conocimiento que se provee. "
            "No agregues información que no esté en estos fragmentos.\n\n"
            "## BASE DE CONOCIMIENTO\n"
            f"{context_str}\n\n"
            "## INSTRUCCIONES\n"
            "- Basá tu respuesta únicamente en la información provista arriba\n"
            "- Si la información no cubre completamente la pregunta, indicalo con honestidad\n"
            "- No inventes datos, precios, porcentajes ni condiciones que no estén en el texto\n"
            "- Respondé de forma natural y conversacional, no como una lectura literal del texto\n"
            "- Si hay información de varias fuentes, integrala en una respuesta coherente"
        )

    def _block_fallback(self) -> str:
        return (
            "## TAREA\n"
            "El mensaje del usuario no se pudo clasificar claramente. "
            "Respondé de forma amable, mostrá disposición a ayudar, "
            "y guiá al usuario a especificar qué tipo de propiedad busca o qué necesita."
        )

    # ─── Construcción de mensajes ──────────────────────────────────────────────

    def _build_messages(self, turn: TurnContext) -> list[dict]:
        """
        Construye el historial de mensajes para Anthropic a partir de
        mensajes_recientes (ya en formato {"role": ..., "content": ...}).

        mensajes_recientes son los mensajes PREVIOS al turno actual
        (context_manager los carga antes de persistir el mensaje actual).

        Garantías:
          - El primer mensaje es siempre "user"
          - Los roles alternan estrictamente (requerido por Anthropic)
          - El mensaje actual del usuario va siempre al final
        """
        previos = [
            m for m in (turn.mensajes_recientes or [])
            if m.get("content", "").strip()
        ]

        # Garantizar alternancia fusionando consecutivos del mismo rol
        alternados: list[dict] = []
        for msg in previos:
            role = msg.get("role", "user")
            content = msg.get("content", "").strip()
            if alternados and alternados[-1]["role"] == role:
                alternados[-1]["content"] += f"\n{content}"
            else:
                alternados.append({"role": role, "content": content})

        # El primer mensaje debe ser "user"
        while alternados and alternados[0]["role"] != "user":
            alternados.pop(0)

        # Agregar mensaje actual
        current = turn.mensaje.strip()
        if alternados and alternados[-1]["role"] == "user":
            # Fusionar si el último también es "user" (caso raro)
            alternados[-1]["content"] += f"\n{current}"
        else:
            alternados.append({"role": "user", "content": current})

        return alternados if alternados else [{"role": "user", "content": current}]

    # ─── Helpers de formato ───────────────────────────────────────────────────

    def _format_items_for_prompt(self, items: list[ItemCandidate]) -> str:
        """Serializa los items como texto estructurado para el prompt de búsqueda."""
        lines = []
        for i, it in enumerate(items, 1):
            atrib = it.atributos or {}
            barrio = atrib.get("barrio") or atrib.get("ciudad") or ""
            calle = atrib.get("calle") or ""
            dorms = atrib.get("dormitorios")
            banios = atrib.get("banios")
            sup_cub = atrib.get("superficie_cubierta")
            detalles = atrib.get("detalles") or []

            precio_str = ""
            if it.precio and it.precio > 0:
                precio_str = f"{it.moneda or 'USD'} {int(it.precio):,}".replace(",", ".")

            ubicacion = " — ".join(filter(None, [calle, barrio]))
            attrs = []
            if dorms:
                attrs.append(f"{dorms} dorm.")
            if banios:
                attrs.append(f"{banios} baños")
            if sup_cub:
                attrs.append(str(sup_cub))
            if precio_str:
                attrs.append(precio_str)
            elif it.descripcion_corta:
                attrs.append(it.descripcion_corta[:70])
            if detalles:
                attrs.append(f"[{', '.join(detalles[:4])}]")

            linea = f"{i}. {it.titulo}"
            if ubicacion:
                linea += f" | {ubicacion}"
            if attrs:
                linea += " | " + " | ".join(attrs)
            lines.append(linea)

        return "\n".join(lines)

    def _ultimo_item_titulo(self, state: ConversationState) -> str | None:
        """Devuelve el título del último item referenciado, o None si no aplica."""
        if not state.ultimo_item_referenciado or not state.items_recientes_resumen:
            return None
        for it in state.items_recientes_resumen:
            if it.id_item == state.ultimo_item_referenciado:
                return it.titulo
        return None

    def _filtros_str(self, filters_activos: dict) -> str:
        """Resumen textual de filtros activos para mensajes de 0 resultados."""
        parts = []
        if filters_activos.get("tipo"):
            parts.append(filters_activos["tipo"])
        if filters_activos.get("zona"):
            parts.append(f"en {filters_activos['zona']}")
        atrib = filters_activos.get("atributos", {})
        for k, v in atrib.items():
            if v is True:
                parts.append(f"con {k}")
            elif isinstance(v, int):
                parts.append(f"{k}={v}")
        if filters_activos.get("precio_max"):
            m = filters_activos.get("moneda", "USD")
            parts.append(f"hasta {m} {int(filters_activos['precio_max']):,}".replace(",", "."))
        return ", ".join(parts)
