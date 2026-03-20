"""
SQLAlchemy ORM — mapeo completo de tablas de la plataforma InmoBot Premium.

Notas:
- conversaciones.id_lead es nullable: la conversación se crea al primer mensaje,
  el lead se vincula solo cuando hay señal comercial.
- contextos_conversacion incluye estado_json (JSONB) para el estado estructurado.
- Las tablas premium_* están creadas en la DB aunque no figuren en el DDL original.
"""
import uuid
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ─── RUBROS ──────────────────────────────────────────────────────────────────

class Rubro(Base):
    __tablename__ = "rubros"

    id_rubro: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    schema: Mapped["RubroSchema | None"] = relationship("RubroSchema", back_populates="rubro", uselist=False)
    prompts: Mapped[list["RubroPrompt"]] = relationship("RubroPrompt", back_populates="rubro")


# ─── PLANES ──────────────────────────────────────────────────────────────────

class Plan(Base):
    __tablename__ = "planes"

    id_plan: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    followup_habilitado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ia_habilitada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_leads_mes: Mapped[int | None] = mapped_column(Integer)
    max_mensajes_mes: Mapped[int | None] = mapped_column(Integer)
    max_items: Mapped[int | None] = mapped_column(Integer)
    max_kb_docs: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ─── EMPRESAS ────────────────────────────────────────────────────────────────

class Empresa(Base):
    __tablename__ = "empresas"

    id_empresa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    # id_rubro NO está en empresas — se define en empresa_rubros (ver EmpresaRubro)
    id_plan: Mapped[int | None] = mapped_column(Integer, ForeignKey("planes.id_plan", ondelete="RESTRICT"))
    permite_followup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    timezone: Mapped[str] = mapped_column(Text, nullable=False, default="America/Argentina/Buenos_Aires")
    slug: Mapped[str | None] = mapped_column(Text, unique=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_empresas_plan", "id_plan"),
    )

    plan: Mapped["Plan | None"] = relationship("Plan")
    rubros_empresa: Mapped[list["EmpresaRubro"]] = relationship("EmpresaRubro", back_populates="empresa")
    prompt_override: Mapped["EmpresaPromptOverride | None"] = relationship(
        "EmpresaPromptOverride", back_populates="empresa", uselist=False,
        primaryjoin="and_(Empresa.id_empresa == EmpresaPromptOverride.id_empresa, EmpresaPromptOverride.activo == True)"
    )


# ─── EMPRESA_RUBROS ───────────────────────────────────────────────────────────
# Relación muchos-a-muchos: una empresa puede operar en varios rubros.
# es_default=True identifica el rubro principal de la empresa.

class EmpresaRubro(Base):
    __tablename__ = "empresa_rubros"

    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), primary_key=True)
    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), primary_key=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    es_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="rubros_empresa")
    rubro: Mapped["Rubro"] = relationship("Rubro")


# ─── EMPRESA_RUBRO_CATALOGOS ──────────────────────────────────────────────────
# Config del catálogo (fuente de datos) por empresa + rubro.

class EmpresaRuboCatalogo(Base):
    __tablename__ = "empresa_rubro_catalogos"

    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), primary_key=True)
    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), primary_key=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    catalog_source: Mapped[str | None] = mapped_column(Text)   # 'github_json', 'db', etc.
    export_format: Mapped[str | None] = mapped_column(Text)
    github_repo: Mapped[str | None] = mapped_column(Text)
    github_branch: Mapped[str | None] = mapped_column(Text)
    github_path: Mapped[str | None] = mapped_column(Text)
    github_raw_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ─── ITEMS ───────────────────────────────────────────────────────────────────

class Item(Base):
    __tablename__ = "items"

    id_item: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str | None] = mapped_column(Text)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    descripcion_corta: Mapped[str | None] = mapped_column(Text)
    precio: Mapped[float | None] = mapped_column(Numeric)
    moneda: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    destacado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    atributos: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    media: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_items_empresa_activo", "id_empresa", "activo"),
        Index("idx_items_empresa_rubro", "id_empresa", "id_rubro"),
    )


# ─── KB_DOCUMENTS ─────────────────────────────────────────────────────────────

class KBDocument(Base):
    __tablename__ = "kb_documents"

    id_documento: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    contenido_texto: Mapped[str | None] = mapped_column(Text)
    storage_url: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chunks: Mapped[list["KBChunk"]] = relationship("KBChunk", back_populates="documento", cascade="all, delete-orphan")


class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id_chunk: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_documento: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kb_documents.id_documento", ondelete="CASCADE"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_texto: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    documento: Mapped["KBDocument"] = relationship("KBDocument", back_populates="chunks")


# ─── RUBRO_SCHEMA ─────────────────────────────────────────────────────────────

class RubroSchema(Base):
    __tablename__ = "rubro_schema"

    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), primary_key=True)
    search_mode: Mapped[str] = mapped_column(Text, nullable=False)
    required_keys: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    facet_keys: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    validation_rules: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    rubro: Mapped["Rubro"] = relationship("Rubro", back_populates="schema")


# ─── RUBRO_PROMPTS ────────────────────────────────────────────────────────────

class RubroPrompt(Base):
    __tablename__ = "rubro_prompts"

    id_prompt: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rubro: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id_rubro", ondelete="RESTRICT"), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    style_prompt: Mapped[str | None] = mapped_column(Text)
    tooling_prompt: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("id_rubro", "version", name="uq_rubro_version"),
        Index("idx_rubro_prompts_activo", "id_rubro", "activo"),
    )

    rubro: Mapped["Rubro"] = relationship("Rubro", back_populates="prompts")


# ─── EMPRESA_PROMPT_OVERRIDES ─────────────────────────────────────────────────

class EmpresaPromptOverride(Base):
    __tablename__ = "empresa_prompt_overrides"

    id_override: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    prompt_extra: Mapped[str | None] = mapped_column(Text)
    brand_voice: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="prompt_override")


# ─── LEADS ────────────────────────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"

    id_lead: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str | None] = mapped_column(Text)
    telefono: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    canal: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Text, nullable=False, default="nuevo")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_leads_empresa_fecha", "id_empresa", "created_at"),
        Index("idx_leads_empresa_estado", "id_empresa", "estado"),
    )

    conversaciones: Mapped[list["Conversacion"]] = relationship("Conversacion", back_populates="lead")
    followups: Mapped[list["Followup"]] = relationship("Followup", back_populates="lead")


# ─── CONVERSACIONES ───────────────────────────────────────────────────────────

class Conversacion(Base):
    __tablename__ = "conversaciones"

    id_conversacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # id_lead es nullable: se vincula cuando existe señal comercial suficiente
    id_lead: Mapped[int | None] = mapped_column(Integer, ForeignKey("leads.id_lead", ondelete="CASCADE"), nullable=True)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    canal: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[str | None] = mapped_column(Text, index=True)
    inicio: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
    fin: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_conv_empresa_fecha", "id_empresa", "created_at"),
        Index("idx_conv_lead_fecha", "id_lead", "created_at"),
    )

    lead: Mapped["Lead | None"] = relationship("Lead", back_populates="conversaciones")
    mensajes: Mapped[list["Mensaje"]] = relationship("Mensaje", back_populates="conversacion", cascade="all, delete-orphan")
    contexto: Mapped["ContextoConversacion | None"] = relationship("ContextoConversacion", back_populates="conversacion", uselist=False)
    followups: Mapped[list["Followup"]] = relationship("Followup", back_populates="conversacion")


# ─── MENSAJES ─────────────────────────────────────────────────────────────────

class Mensaje(Base):
    __tablename__ = "mensajes"

    id_mensaje: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_conversacion: Mapped[int] = mapped_column(Integer, ForeignKey("conversaciones.id_conversacion", ondelete="CASCADE"), nullable=False)
    emisor: Mapped[str] = mapped_column(Text, nullable=False)  # 'user' | 'bot' | 'system'
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    timestamp: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("emisor IN ('user', 'bot', 'system')", name="chk_mensajes_emisor"),
        Index("idx_mensajes_conv_ts", "id_conversacion", "timestamp"),
    )

    conversacion: Mapped["Conversacion"] = relationship("Conversacion", back_populates="mensajes")


# ─── FOLLOWUPS ────────────────────────────────────────────────────────────────

class Followup(Base):
    __tablename__ = "followups"

    id_followup: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_lead: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id_lead", ondelete="CASCADE"), nullable=False)
    id_conversacion: Mapped[int | None] = mapped_column(Integer, ForeignKey("conversaciones.id_conversacion", ondelete="SET NULL"))
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(Text, nullable=False, default="pendiente")
    fecha_programada: Mapped[Any] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_ejecucion: Mapped[Any | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'enviado', 'cancelado', 'fallido')",
            name="chk_followups_estado",
        ),
        Index("idx_followups_pendientes", "fecha_programada"),
        Index("idx_followups_lead", "id_lead", "created_at"),
    )

    lead: Mapped["Lead"] = relationship("Lead", back_populates="followups")
    conversacion: Mapped["Conversacion | None"] = relationship("Conversacion", back_populates="followups")


# ─── CONTEXTOS_CONVERSACION ───────────────────────────────────────────────────

class ContextoConversacion(Base):
    __tablename__ = "contextos_conversacion"

    id_contexto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_conversacion: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversaciones.id_conversacion", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    resumen_contexto: Mapped[str | None] = mapped_column(Text)
    # estado_json almacena el ConversationState estructurado
    estado_json: Mapped[dict | None] = mapped_column(JSONB)
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    conversacion: Mapped["Conversacion"] = relationship("Conversacion", back_populates="contexto")


# ─── PREMIUM_CHAT_LOGS ────────────────────────────────────────────────────────

class PremiumChatLog(Base):
    __tablename__ = "premium_chat_logs"

    id_log: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    id_conversacion: Mapped[int | None] = mapped_column(Integer, ForeignKey("conversaciones.id_conversacion", ondelete="SET NULL"))
    session_id: Mapped[str | None] = mapped_column(Text)
    canal: Mapped[str | None] = mapped_column(Text)
    route_elegida: Mapped[str | None] = mapped_column(Text)
    intent_detectada: Mapped[str | None] = mapped_column(Text)
    hubo_fallback_ia: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    model_usado: Mapped[str | None] = mapped_column(Text)
    tokens_input: Mapped[int | None] = mapped_column(Integer)
    tokens_output: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    items_mostrados_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_pcl_empresa_fecha", "id_empresa", "created_at"),
    )

    items: Mapped[list["PremiumChatLogItem"]] = relationship("PremiumChatLogItem", back_populates="chat_log", cascade="all, delete-orphan")


class PremiumChatLogItem(Base):
    __tablename__ = "premium_chat_log_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_log: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("premium_chat_logs.id_log", ondelete="CASCADE"), nullable=False)
    id_item: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id_item", ondelete="CASCADE"), nullable=False)
    posicion: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat_log: Mapped["PremiumChatLog"] = relationship("PremiumChatLog", back_populates="items")


# ─── PREMIUM_CONVERSION_LOGS ──────────────────────────────────────────────────

class PremiumConversionLog(Base):
    __tablename__ = "premium_conversion_logs"

    id_conversion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    id_conversacion: Mapped[int | None] = mapped_column(Integer, ForeignKey("conversaciones.id_conversacion", ondelete="SET NULL"))
    id_lead: Mapped[int | None] = mapped_column(Integer, ForeignKey("leads.id_lead", ondelete="SET NULL"))
    # Ej: 'lead_created', 'asesor_requested', 'visita_requested', 'item_detail_viewed', 'contacto_confirmado'
    evento: Mapped[str] = mapped_column(Text, nullable=False)
    route: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_pcvl_empresa_fecha", "id_empresa", "created_at"),
        Index("idx_pcvl_empresa_evento", "id_empresa", "evento"),
    )

    items: Mapped[list["PremiumConversionLogItem"]] = relationship("PremiumConversionLogItem", back_populates="conversion_log", cascade="all, delete-orphan")


class PremiumConversionLogItem(Base):
    __tablename__ = "premium_conversion_log_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_conversion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("premium_conversion_logs.id_conversion", ondelete="CASCADE"), nullable=False)
    id_item: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id_item", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversion_log: Mapped["PremiumConversionLog"] = relationship("PremiumConversionLog", back_populates="items")
