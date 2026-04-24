"""
Pydantic schemas para requests y responses de la API.
"""
import uuid
from typing import Any

from pydantic import BaseModel, Field


# ─── CHAT ─────────────────────────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    """Payload del endpoint principal POST /chat/message."""
    empresa_slug: str = Field(..., description="Slug único de la empresa (tenant)")
    canal: str = Field(..., description="Canal de entrada: 'web' | 'whatsapp' | 'instagram'")
    session_id: str = Field(..., description="ID de sesión del usuario en el canal")
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata adicional del canal")


class ItemBrief(BaseModel):
    """Resumen de un item para incluir en la respuesta conversacional."""
    id_item: str
    titulo: str
    tipo: str = ""      # 'casa' | 'departamento' | 'local' | etc.
    categoria: str = "" # 'venta' | 'alquiler' | etc.
    precio: float | None = None
    moneda: str | None = None
    descripcion_corta: str | None = None
    fotos: list[str] = []
    atributos: dict[str, Any] = {}


class ChatMessageResponse(BaseModel):
    """Respuesta del endpoint principal POST /chat/message."""
    session_id: str
    conversation_id: int | None = None
    respuesta: str
    items: list[ItemBrief] = []
    route: str
    stage: str
    lead_capturado: bool = False
    metadata: dict[str, Any] = {}


# ─── WEBHOOKS ─────────────────────────────────────────────────────────────────

class WebhookWidgetPayload(BaseModel):
    """
    Payload recibido desde el widget web (formato legacy).
    Usado solo por webhook_widget.py; la traducción la hace widget_legacy.py.
    """
    message: str = Field(..., min_length=1, max_length=2000)
    sessionId: str
    timestamp: str = Field(default="")
    repo: str = Field(default="")


class WebhookWhatsAppPayload(BaseModel):
    """Payload normalizado recibido desde WhatsApp Business."""
    empresa_slug: str
    phone_number: str
    message_id: str
    mensaje: str
    metadata: dict[str, Any] = {}


# ─── CATÁLOGO ─────────────────────────────────────────────────────────────────

class ItemResponse(BaseModel):
    """Representación completa de un item del catálogo."""
    id_item: str
    id_empresa: int
    id_rubro: int
    tipo: str
    categoria: str | None
    titulo: str
    descripcion: str | None
    descripcion_corta: str | None
    precio: float | None
    moneda: str | None
    activo: bool
    destacado: bool
    atributos: dict[str, Any]
    media: dict[str, Any]


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int


# ─── LEADS ────────────────────────────────────────────────────────────────────

class LeadCreateRequest(BaseModel):
    id_empresa: int
    nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
    canal: str | None = None
    metadata: dict[str, Any] = {}


class LeadUpdateRequest(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
    estado: str | None = None
    metadata: dict[str, Any] | None = None


class LeadResponse(BaseModel):
    id_lead: int
    id_empresa: int
    nombre: str | None
    telefono: str | None
    email: str | None
    canal: str | None
    estado: str
    metadata: dict[str, Any]
    created_at: str | None = None


class LeadListResponse(BaseModel):
    leads: list[LeadResponse]
    total: int
    page: int = 1
    page_size: int = 20


class PropiedadDetalle(BaseModel):
    id: str
    titulo: str
    tipo: str | None = None
    categoria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    barrio: str | None = None
    dormitorios: int | None = None
    banios: int | None = None
    superficie_cubierta: str | None = None


class LeadDetailResponse(LeadResponse):
    propiedades_detalle: list[PropiedadDetalle] = []


# ─── ITEMS (ADMIN) ────────────────────────────────────────────────────────────

class ItemAdminResponse(BaseModel):
    id_item: str
    external_id: str
    tipo: str
    categoria: str | None
    titulo: str
    descripcion: str | None
    descripcion_corta: str | None
    precio: float | None
    moneda: str | None
    activo: bool
    destacado: bool
    atributos: dict[str, Any]
    media: dict[str, Any]
    created_at: str | None = None


class ItemAdminListResponse(BaseModel):
    items: list[ItemAdminResponse]
    total: int
    page: int
    page_size: int


class ItemCreateRequest(BaseModel):
    tipo: str
    categoria: str | None = None
    titulo: str
    descripcion: str | None = None
    descripcion_corta: str | None = None
    precio: float | None = None
    moneda: str | None = None
    destacado: bool = False
    atributos: dict[str, Any] = {}
    fotos: list[str] = []


class ItemUpdateRequest(BaseModel):
    external_id: str | None = None
    tipo: str | None = None
    categoria: str | None = None
    titulo: str | None = None
    descripcion: str | None = None
    descripcion_corta: str | None = None
    precio: float | None = None
    moneda: str | None = None
    activo: bool | None = None
    destacado: bool | None = None
    atributos: dict[str, Any] | None = None
    fotos: list[str] | None = None


class CloudinarySignResponse(BaseModel):
    cloud_name: str
    api_key: str
    timestamp: int
    signature: str
    folder: str
    transformation: str = ""


class ExportLandingResponse(BaseModel):
    ok: bool
    total: int
    commit_sha: str | None = None
    message: str


# ─── ANALYTICS ────────────────────────────────────────────────────────────────

class ChatLogResponse(BaseModel):
    id_log: str
    id_empresa: int
    session_id: str | None
    canal: str | None
    consulta: str | None
    success: bool
    model: str | None
    tokens_input: int | None
    tokens_output: int | None
    response_time_ms: int | None
    items_mostrados: int
    created_at: str


class ConversionLogResponse(BaseModel):
    id_conversion: str
    id_empresa: int
    id_lead: int | None
    event_type: str
    payload: dict[str, Any]
    created_at: str


class AnalyticsSummaryResponse(BaseModel):
    total_chats: int
    total_conversiones: int
    total_leads: int
    routes_distribution: dict[str, int]
    conversion_events_distribution: dict[str, int]
    avg_response_time_ms: float | None
    periodo: str


# ─── EMPRESAS (ADMIN) ────────────────────────────────────────────────────────

class EmpresaServiciosSchema(BaseModel):
    bot: bool = True
    landing: bool = False
    catalogo_repo: bool = False
    panel_cliente: bool = False
    instagram: bool = False
    facebook: bool = False

class EmpresaTelegramSchema(BaseModel):
    enabled: bool = False
    chat_id: str = ""

class EmpresaEmailSchema(BaseModel):
    enabled: bool = False
    to: str = ""

class EmpresaNotificacionesSchema(BaseModel):
    telegram: EmpresaTelegramSchema = EmpresaTelegramSchema()
    email: EmpresaEmailSchema = EmpresaEmailSchema()

class EmpresaAdminResponse(BaseModel):
    id_empresa: int
    nombre: str
    slug: str | None
    id_plan: int | None
    activa: bool
    permite_followup: bool
    timezone: str
    servicios: EmpresaServiciosSchema
    notificaciones: EmpresaNotificacionesSchema
    created_at: str | None = None

class EmpresaListResponse(BaseModel):
    empresas: list[EmpresaAdminResponse]
    total: int

class EmpresaCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=3)
    slug: str = Field(..., min_length=2, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    id_plan: int = 1
    id_rubro: int = 1
    timezone: str = "America/Argentina/Buenos_Aires"
    activa: bool = True

class EmpresaUpdateRequest(BaseModel):
    nombre: str | None = Field(None, min_length=3)
    id_plan: int | None = None
    activa: bool | None = None
    permite_followup: bool | None = None
    timezone: str | None = None
    servicios: EmpresaServiciosSchema | None = None
    notificaciones: EmpresaNotificacionesSchema | None = None

class CatalogoRepoResponse(BaseModel):
    id_empresa: int
    id_rubro: int
    activo: bool
    catalog_source: str | None
    export_format: str | None
    github_repo: str | None
    github_branch: str | None
    github_path: str | None
    github_raw_url: str | None

class CatalogoRepoUpdateRequest(BaseModel):
    github_repo: str | None = None
    github_branch: str | None = None
    github_path: str | None = None
    github_raw_url: str | None = None
    catalog_source: str | None = None
    export_format: str | None = None


# ─── USUARIOS (ADMIN) ────────────────────────────────────────────────────────

class UsuarioAdminResponse(BaseModel):
    id_usuario: int
    nombre: str | None
    email: str
    es_superadmin: bool
    activo: bool
    id_empresa: int | None
    empresa_nombre: str | None
    created_at: str | None = None

class UsuarioListResponse(BaseModel):
    usuarios: list[UsuarioAdminResponse]
    total: int

class UsuarioCreateRequest(BaseModel):
    nombre: str | None = Field(None, min_length=2)
    email: str
    password: str = Field(..., min_length=8)
    es_superadmin: bool = False
    id_empresa: int | None = None

class UsuarioUpdateRequest(BaseModel):
    nombre: str | None = None
    email: str | None = None
    es_superadmin: bool | None = None
    id_empresa: int | None = None
    activo: bool | None = None

class UsuarioResetPasswordRequest(BaseModel):
    nueva_password: str = Field(..., min_length=8)


# ─── IMPORTACIONES (ADMIN) ───────────────────────────────────────────────────

class ImportacionPreviewRequest(BaseModel):
    id_empresa: int
    catalogo: dict[str, Any]

class ImportacionPreviewItem(BaseModel):
    external_id: str
    titulo: str
    tipo: str
    categoria: str | None

class ImportacionItemModificado(ImportacionPreviewItem):
    cambios: list[str]

class ImportacionPreviewResponse(BaseModel):
    id_empresa: int
    total_json: int
    total_db: int
    nuevos: list[ImportacionPreviewItem]
    modificados: list[ImportacionItemModificado]
    sin_cambios: int
    a_desactivar: list[ImportacionPreviewItem]

class ImportacionAplicarRequest(BaseModel):
    id_empresa: int
    catalogo: dict[str, Any]

class ImportacionAplicarResponse(BaseModel):
    ok: bool
    insertados: int
    actualizados: int
    desactivados: int
    id_log: int
    message: str

class ImportacionPublicarRequest(BaseModel):
    id_empresa: int

class ImportacionPublicarResponse(BaseModel):
    ok: bool
    total: int
    commit_sha: str | None = None
    id_log: int
    message: str

class ImportacionLogResponse(BaseModel):
    id: int
    id_empresa: int
    empresa_nombre: str | None
    accion: str
    resultado: str
    detalle: dict[str, Any]
    nombre_usuario: str | None
    created_at: str | None

class ImportacionLogListResponse(BaseModel):
    logs: list[ImportacionLogResponse]
    total: int


# ─── HEALTH ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    db: str = "unknown"
