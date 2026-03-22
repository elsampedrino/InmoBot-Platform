"""
Objetos internos del dominio. No son ORM ni Pydantic de API.
Son las estructuras que circulan entre services durante el pipeline.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class Route(str, Enum):
    SALUDO                = "saludo"
    BUSCAR_CATALOGO       = "buscar_catalogo"
    REFINAR_BUSQUEDA      = "refinar_busqueda"
    VER_DETALLE_ITEM      = "ver_detalle_item"
    COMPARAR_ITEMS        = "comparar_items"
    PREGUNTA_KB           = "pregunta_kb"
    INFORMACION_EMPRESA   = "informacion_empresa"
    CAPTURAR_LEAD         = "capturar_lead"
    CONTACTAR_ASESOR      = "contactar_asesor"
    AGENDAR_VISITA        = "agendar_visita"
    FOLLOWUP              = "followup"
    SMALLTALK             = "smalltalk_controlado"
    FALLBACK              = "fallback"


class ConversationStage(str, Enum):
    INICIO      = "inicio"
    EXPLORACION = "exploracion"
    INTERES     = "interes"
    CONVERSION  = "conversion"
    CERRADA     = "cerrada"


class ConversionEvent(str, Enum):
    LEAD_CREATED         = "lead_created"
    LEAD_UPDATED         = "lead_updated"
    ASESOR_REQUESTED     = "asesor_requested"
    VISITA_REQUESTED     = "visita_requested"
    ITEM_DETAIL_VIEWED   = "item_detail_viewed"
    ITEM_SHARED          = "item_shared"
    CONTACTO_CONFIRMADO  = "contacto_confirmado"


# ─── FILTROS DE BÚSQUEDA ──────────────────────────────────────────────────────

@dataclass
class SearchFilters:
    """Salida del QueryParser. Entrada del SearchEngine."""
    tipo: str | None = None
    categoria: str | None = None
    zona: str | None = None
    precio_min: float | None = None
    precio_max: float | None = None
    moneda: str | None = None
    atributos: dict[str, Any] = field(default_factory=dict)
    # Texto libre para full-text search como fallback
    texto_libre: str | None = None

    def has_useful_filters(self) -> bool:
        """
        True si el filtro contiene al menos un criterio explícito del usuario,
        más allá de id_empresa / id_rubro / activo (que son siempre implícitos).

        Usado por SearchEngine para detectar búsquedas sin contexto y aplicar
        la regla de catálogo-de-inicio (máx. _MAX_ITEMS_NO_FILTERS items).
        """
        return bool(
            self.tipo
            or self.categoria
            or self.zona
            or self.precio_min is not None
            or self.precio_max is not None
            or self.atributos
            or self.texto_libre
        )


# ─── ITEMS ────────────────────────────────────────────────────────────────────

@dataclass
class ItemCandidate:
    """Item devuelto por el SearchEngine para ser enviado a la IA."""
    id_item: str
    titulo: str
    descripcion_corta: str | None
    precio: float | None
    moneda: str | None
    atributos: dict[str, Any]
    fotos: list[str]
    destacado: bool
    tipo: str = ""        # columna top-level: 'casa' | 'departamento' | etc.
    categoria: str = ""   # columna top-level: 'venta' | 'alquiler' | etc.
    score: float = 0.0


@dataclass
class ItemSummary:
    """Referencia mínima a un item para el estado conversacional."""
    id_item: str
    label: str        # "opcion_1", "opcion_2", etc.
    titulo: str


# ─── ESTADO CONVERSACIONAL ────────────────────────────────────────────────────

@dataclass
class ConversationState:
    """
    Estado estructurado persistido en contextos_conversacion.estado_json.
    Permite al router tomar decisiones consistentes entre turnos.
    """
    conversation_stage: ConversationStage = ConversationStage.INICIO
    route_actual: str | None = None
    intent_previa: str | None = None

    # Filtros activos de la búsqueda en curso
    filters_activos: dict[str, Any] = field(default_factory=dict)

    # Referencias a items mostrados en la conversación
    items_recientes: list[str] = field(default_factory=list)
    items_recientes_resumen: list[ItemSummary] = field(default_factory=list)
    ultimo_item_referenciado: str | None = None
    comparacion_activa: bool = False

    # Señales comerciales
    lead_capturado: bool = False
    advisor_requested: bool = False
    visit_requested: bool = False

    # Esperas operativas (el bot hizo una pregunta y espera un dato)
    esperando_contacto: bool = False
    esperando_visita: bool = False
    esperando_confirmacion: bool = False

    last_user_message_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "conversation_stage": self.conversation_stage.value,
            "route_actual": self.route_actual,
            "intent_previa": self.intent_previa,
            "filters_activos": self.filters_activos,
            "items_recientes": self.items_recientes,
            "items_recientes_resumen": [
                {"id_item": i.id_item, "label": i.label, "titulo": i.titulo}
                for i in self.items_recientes_resumen
            ],
            "ultimo_item_referenciado": self.ultimo_item_referenciado,
            "comparacion_activa": self.comparacion_activa,
            "lead_capturado": self.lead_capturado,
            "advisor_requested": self.advisor_requested,
            "visit_requested": self.visit_requested,
            "esperando_contacto": self.esperando_contacto,
            "esperando_visita": self.esperando_visita,
            "esperando_confirmacion": self.esperando_confirmacion,
            "last_user_message_at": self.last_user_message_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationState":
        items_resumen = [
            ItemSummary(id_item=i["id_item"], label=i["label"], titulo=i["titulo"])
            for i in data.get("items_recientes_resumen", [])
        ]
        return cls(
            conversation_stage=ConversationStage(data.get("conversation_stage", "inicio")),
            route_actual=data.get("route_actual"),
            intent_previa=data.get("intent_previa"),
            filters_activos=data.get("filters_activos", {}),
            items_recientes=data.get("items_recientes", []),
            items_recientes_resumen=items_resumen,
            ultimo_item_referenciado=data.get("ultimo_item_referenciado"),
            comparacion_activa=data.get("comparacion_activa", False),
            lead_capturado=data.get("lead_capturado", False),
            advisor_requested=data.get("advisor_requested", False),
            visit_requested=data.get("visit_requested", False),
            esperando_contacto=data.get("esperando_contacto", False),
            esperando_visita=data.get("esperando_visita", False),
            esperando_confirmacion=data.get("esperando_confirmacion", False),
            last_user_message_at=data.get("last_user_message_at"),
        )


# ─── DECISIÓN DEL ROUTER ──────────────────────────────────────────────────────

@dataclass
class RouterActions:
    run_parser: bool = False
    run_search: bool = False
    run_kb_search: bool = False
    run_ai_response: bool = True
    create_or_update_lead: bool = False
    register_conversion_event: bool = False
    conversion_event: ConversionEvent | None = None


@dataclass
class RouterDecision:
    route: Route
    intent: str
    confidence: float
    used_ai_fallback: bool
    entities: dict[str, Any]
    actions: RouterActions
    business_signals: dict[str, Any] = field(default_factory=dict)


# ─── CONTEXTO DEL TURNO ───────────────────────────────────────────────────────

@dataclass
class TenantConfig:
    """Configuración resuelta de empresa + rubro para el turno."""
    id_empresa: int
    id_rubro: int
    nombre_empresa: str
    slug: str | None
    system_prompt: str
    style_prompt: str | None
    brand_voice: str | None
    prompt_extra: str | None
    max_items_per_response: int
    ia_habilitada: bool
    followup_habilitado: bool
    search_mode: str   # 'items_structured' | 'kb_text' | 'mixed'
    facet_keys: list[str]
    validation_rules: dict[str, Any]


@dataclass
class TurnContext:
    """Todo lo necesario para procesar un turno conversacional."""
    id_empresa: int
    id_rubro: int
    canal: str
    session_id: str
    mensaje: str
    id_conversacion: int | None
    conversation_state: ConversationState
    resumen_contexto: str | None
    mensajes_recientes: list[dict[str, Any]]
    tenant_config: TenantConfig


# ─── RESULTADO DEL SEARCH ENGINE ──────────────────────────────────────────────

@dataclass
class SearchResult:
    items: list[ItemCandidate]
    total_encontrados: int
    facets: dict[str, Any] = field(default_factory=dict)
    search_narrowed: bool = False   # True si se redujo el scope


# ─── RESPUESTA ENSAMBLADA ─────────────────────────────────────────────────────

@dataclass
class AssembledResponse:
    respuesta: str
    items: list[ItemCandidate]
    route: Route
    stage: ConversationStage
    lead_capturado: bool
    metadata: dict[str, Any] = field(default_factory=dict)
