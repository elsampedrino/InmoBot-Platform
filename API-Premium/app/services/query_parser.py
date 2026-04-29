"""
QueryParser — traduce lenguaje natural a SearchFilters estructurados.

Responsabilidades:
- Detectar tipo, categoría, zona, precio, moneda y atributos del mensaje
- Normalizar sinónimos y variantes del lenguaje rioplatense
- Combinar con filtros activos del contexto en caso de refinamiento
- Producir un SearchFilters listo para el SearchEngine

Estrategia:
- Reglas determinísticas + diccionarios (sin IA)
- Refinamientos: merge con filters_activos (nuevo tiene precedencia)
- "más barato" / "más caro": ajusta el precio activo en ±25%

No debe:
- Decidir la ruta operativa
- Ejecutar búsquedas
- Generar texto al usuario
"""
import re

from app.core.logging import get_logger
from app.models.domain_models import ConversationState, SearchFilters

logger = get_logger(__name__)

# ─── Diccionarios de normalización ────────────────────────────────────────────

_TIPO_MAP: dict[str, list[str]] = {
    "departamento":  ["departamento", "departamentos", "depto", "deptos", "dpto", "dptos"],
    "casa":          ["casa", "casas", "chalet", "chalets"],
    "ph":            ["ph", "penthouse"],
    "terreno":       ["lote", "lotes", "terreno", "terrenos"],
    "campo":         ["campo", "campos", "chacra", "chacras", "estancia"],
    "local comercial": ["local", "locales", "comercial", "oficina", "oficinas"],
    "cochera":       ["cochera", "cocheras", "garage", "garaje"],
    "galpon":        ["galpon", "galpón", "galpones"],
}

_CATEG_MAP: dict[str, list[str]] = {
    "venta":              ["venta", "vender", "comprar", "compro", "compra"],
    "alquiler":           ["alquiler", "alquilar", "alquilo", "renta"],
    "alquiler_temporario": ["temporario", "temporada", "vacacional"],
}

# Atributos booleanos que se buscan en el array atributos.detalles
_DETALLE_MAP: dict[str, list[str]] = {
    "pileta":    ["pileta", "piletas", "natatorio", "piscina"],
    "cochera":   ["cochera", "cocheras"],
    "balcon":    ["balcon", "balcón", "balcones"],
    "parrilla":  ["parrilla", "parrillas", "quincho", "quinchos"],
    "patio":     ["patio", "patios"],
    "jardin":    ["jardin", "jardín", "jardines"],
    "amenities": ["amenities"],
    "gimnasio":  ["gimnasio", "gym"],
    "seguridad": ["seguridad", "vigilancia", "portero"],
    "ascensor":  ["ascensor", "elevador"],
    "laundry":       ["laundry", "lavadero"],
    "financiacion":  ["financiación", "financiacion", "financiar", "facilidades de pago", "facilidades", "cuotas"],
    "barrio_privado": ["barrio privado", "country", "countries", "barrio cerrado"],
}

# Palabras que "en [X]" NO debe capturar como zona
_ZONA_STOPWORDS = frozenset({
    "venta", "alquiler", "alquiler_temporario", "argentina", "buenos", "aires",
    "la", "el", "los", "las", "del", "zona", "barrio", "ciudad",
    "otra", "otro", "un", "una", "pozo", "construccion", "construcción",
})

# ─── Patrones compilados ──────────────────────────────────────────────────────

_PAT_AMBIENTES = re.compile(r"(\d+)\s*ambientes?", re.IGNORECASE)
_PAT_DORMITORIOS = re.compile(
    r"(\d+)\s*(?:dormitorios?|cuartos?|habitaciones?|rooms?)", re.IGNORECASE
)

# Zona: "en / sobre / cerca de / frente al / junto al [Lugar]"
# El grupo capturado es la keyword geográfica, sin artículo.
# El lookahead (?!...) evita capturar conjunciones (o, y, ni, pero, que, con, sin, por)
# como parte del nombre de zona. Ej: "sobre el río o cerca" → captura solo "río".
_PAT_ZONA = re.compile(
    r"\b(?:en|sobre|cerca\s+de|frente\s+al?|junto\s+al?)\s+"
    r"(?:el?\s+|la?\s+|los?\s+|las?\s+)?"
    r"([A-ZÁÉÍÓÚa-záéíóú][a-záéíóúü]{2,}"
    r"(?:\s+(?!(?:o|y|ni|pero|que|con|sin|por)\b)[A-ZÁÉÍÓÚa-záéíóú][a-záéíóúü]{1,}){0,2})\b"
)

# Precio máximo explícito
_PAT_PRECIO_MAX = re.compile(
    r"\b(?:hasta|menos\s+de|m[aá]x(?:imo)?(?:\s+de)?|presupuesto\s+de)\s+"
    r"(?:(?:usd|u\$s|\$)\s*)?(\d[\d.,]*)\s*(k|mil)?\b",
    re.IGNORECASE,
)
# Precio mínimo explícito
_PAT_PRECIO_MIN = re.compile(
    r"\b(?:desde|m[ií]n(?:imo)?(?:\s+de)?|m[aá]s\s+de)\s+"
    r"(?:usd|u\$s|\$\s*)?(\d[\d.,]*)\s*(k|mil)?\b",
    re.IGNORECASE,
)
# Detección de moneda
_PAT_MONEDA = re.compile(
    r"\b(usd|u\$s|dolar(?:es)?|peso(?:s)?|\$)\b", re.IGNORECASE
)
# Ajustes relativos de precio
_PAT_BARATO = re.compile(
    r"\bm[aá]s\s+(?:barato|econ[oó]mico|accesible|bajo|barata)|"
    r"\bmenor\s+precio|menos\s+caro|algo\s+m[aá]s\s+(?:barato|econ[oó]mico)\b",
    re.IGNORECASE,
)
_PAT_CARO = re.compile(
    r"\bm[aá]s\s+(?:caro|exclusivo|premium|alto|cara)|"
    r"\bmayor\s+precio|algo\s+m[aá]s\s+(?:caro|exclusivo)\b",
    re.IGNORECASE,
)

# Factor de ajuste para "más barato" / "más caro"
_PRICE_ADJUST_FACTOR = 0.75   # "más barato" → max * 0.75

# ─── REGLAS DE NEGOCIO DEL PARSER ────────────────────────────────────────────
# Estas decisiones son explícitas e intencionadas. Cambiarlas tiene impacto
# directo en los resultados de búsqueda.
#
# AMBIENTES  → match exacto (=) en SearchEngine
#   Rationale: en el mercado inmobiliario argentino, "2 ambientes" y "3 ambientes"
#   son categorías distintas. No se amplía el match automáticamente.
#
# DORMITORIOS → mínimo (>=) en SearchEngine
#   Rationale: "quiero 2 dormitorios" significa "al menos 2". Una propiedad con
#   3 dormitorios satisface la búsqueda; lo contrario no es cierto.
#
# PRECIO RELATIVO ("más barato" / "más caro") → ±25% sobre el precio activo
#   Constante: _PRICE_ADJUST_FACTOR = 0.75
#   "más barato" → precio_max * 0.75    (reduce el techo)
#   "más caro"   → precio_min / 0.75    (sube el piso)
#   Solo aplica si hay filters_activos con precio previo.
#
# SIN FILTROS ÚTILES → catálogo de inicio acotado (ver SearchEngine._MAX_ITEMS_NO_FILTERS)
#   Si el parser no extrae tipo, zona, precio ni atributos, SearchEngine devuelve
#   un muestrario inicial en lugar de volcar todo el catálogo sin contexto.
# ─────────────────────────────────────────────────────────────────────────────


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
        msg_lower = mensaje.lower()

        tipo      = self._extract_tipo(msg_lower)
        categoria = self._extract_categoria(msg_lower)
        zona      = self._extract_zona(mensaje)  # preservar case para zona
        atributos = self._extract_atributos(msg_lower)
        precio_min, precio_max, moneda = self._extract_precio(
            msg_lower, state, is_refinement
        )

        new_filters = SearchFilters(
            tipo=tipo,
            categoria=categoria,
            zona=zona,
            precio_min=precio_min,
            precio_max=precio_max,
            moneda=moneda,
            atributos=atributos,
            texto_libre=mensaje if not tipo and not zona and not atributos else None,
        )

        # Mergear con filtros activos si:
        # a) es un refinamiento explícito, O
        # b) el mensaje no aportó ningún filtro nuevo (usuario continúa el contexto)
        new_has_filters = bool(tipo or zona or atributos)
        should_merge = state.filters_activos and (is_refinement or not new_has_filters)
        if should_merge:
            merged = self._merge_with_active_filters(new_filters, state.filters_activos)
            logger.debug(
                "query_parser_refinement",
                active_filters=state.filters_activos,
                new_tipo=tipo,
                new_zona=zona,
                merged_tipo=merged.tipo,
                merged_zona=merged.zona,
            )
            return merged

        logger.debug(
            "query_parser_parsed",
            tipo=tipo,
            categoria=categoria,
            zona=zona,
            precio_min=precio_min,
            precio_max=precio_max,
            moneda=moneda,
            atributos=atributos,
        )
        return new_filters

    # ─── Extractores individuales ──────────────────────────────────────────────

    def _extract_tipo(self, msg: str) -> str | None:
        for tipo, keywords in _TIPO_MAP.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", msg):
                    return tipo
        return None

    def _extract_categoria(self, msg: str) -> str | None:
        for cat, keywords in _CATEG_MAP.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", msg):
                    return cat
        return None

    def _extract_zona(self, mensaje: str) -> str | None:
        """
        Extrae la zona geográfica del patrón "en [Zona]".
        Ignora stopwords y candidatos muy cortos.
        """
        matches = _PAT_ZONA.findall(mensaje)
        for match in matches:
            words = match.strip().lower().split()
            # Excluir si alguna palabra es stopword o el candidato es muy corto
            if any(w in _ZONA_STOPWORDS for w in words):
                continue
            if len(match.strip()) < 3:
                continue
            return match.strip()
        return None

    def _extract_precio(
        self,
        msg: str,
        state: ConversationState,
        is_refinement: bool,
    ) -> tuple[float | None, float | None, str | None]:
        """
        Devuelve (precio_min, precio_max, moneda).
        En refinamiento detecta "más barato" / "más caro" y ajusta los activos.
        """
        # ── Ajuste relativo (refinamiento) ─────────────────────────────────────
        if is_refinement and state.filters_activos:
            active = state.filters_activos
            if _PAT_BARATO.search(msg):
                # Reducir el precio máximo (o crear uno si solo hay mínimo)
                if active.get("precio_max"):
                    return (
                        None,
                        round(active["precio_max"] * _PRICE_ADJUST_FACTOR),
                        active.get("moneda"),
                    )
                elif active.get("precio_min"):
                    return (
                        None,
                        round(active["precio_min"] * _PRICE_ADJUST_FACTOR),
                        active.get("moneda"),
                    )
            elif _PAT_CARO.search(msg):
                if active.get("precio_min"):
                    return (
                        round(active["precio_min"] / _PRICE_ADJUST_FACTOR),
                        None,
                        active.get("moneda"),
                    )

        # ── Precios explícitos ─────────────────────────────────────────────────
        precio_max = self._parse_price_value(_PAT_PRECIO_MAX.search(msg))
        precio_min = self._parse_price_value(_PAT_PRECIO_MIN.search(msg))

        moneda = None
        m = _PAT_MONEDA.search(msg)
        if m:
            raw = m.group(1).lower()
            moneda = "USD" if raw in ("usd", "u$s", "dolar", "dolares") else "ARS"

        return precio_min, precio_max, moneda

    def _extract_atributos(self, msg: str) -> dict:
        """
        Detecta ambientes, dormitorios y atributos booleanos (detalles).
        """
        atributos: dict = {}

        m = _PAT_AMBIENTES.search(msg)
        if m:
            # "X ambientes" → "X-1 dormitorios" (convención argentina:
            # ambientes incluye living; el catálogo almacena solo dormitorios)
            # Solo si no se mencionó dormitorios explícitamente
            if "dormitorios" not in atributos:
                dorms = max(1, int(m.group(1)) - 1)
                atributos["dormitorios"] = dorms

        m = _PAT_DORMITORIOS.search(msg)
        if m:
            atributos["dormitorios"] = int(m.group(1))

        for detalle, keywords in _DETALLE_MAP.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", msg, re.IGNORECASE):
                    atributos[detalle] = True
                    break

        return atributos

    def _merge_with_active_filters(
        self, new_filters: SearchFilters, active: dict
    ) -> SearchFilters:
        """
        Fusiona nuevos filtros con los activos.
        Los nuevos tienen precedencia; los None heredan del activo.
        """
        merged_atributos = dict(active.get("atributos", {}))
        merged_atributos.update(new_filters.atributos)

        return SearchFilters(
            tipo=new_filters.tipo or active.get("tipo"),
            categoria=new_filters.categoria or active.get("categoria"),
            zona=new_filters.zona or active.get("zona"),
            precio_min=(
                new_filters.precio_min
                if new_filters.precio_min is not None
                else active.get("precio_min")
            ),
            precio_max=(
                new_filters.precio_max
                if new_filters.precio_max is not None
                else active.get("precio_max")
            ),
            moneda=new_filters.moneda or active.get("moneda"),
            atributos=merged_atributos,
            texto_libre=new_filters.texto_libre,
        )

    # ─── Helper ────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_price_value(match) -> float | None:
        if not match:
            return None
        val_str = match.group(1).replace(",", "").replace(".", "")
        try:
            val = float(val_str)
            mult = match.group(2)
            if mult and mult.lower() in ("k", "mil"):
                val *= 1000
            return val
        except ValueError:
            return None
