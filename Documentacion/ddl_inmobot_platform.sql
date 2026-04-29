-- =============================================================================
-- DDL InmoBot Platform – PostgreSQL 15+
-- Generado: 2026-02-26
-- Ejecutar contra la base de datos destino (ej: n8n_b4cl o una DB nueva)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 0. EXTENSIONES
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- provee gen_random_uuid()

-- ---------------------------------------------------------------------------
-- 1. FUNCIÓN HELPER PARA updated_at AUTOMÁTICO
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- 2. RUBROS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rubros (
    id_rubro    INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      TEXT        NOT NULL UNIQUE,             -- ej: 'inmobiliaria', 'automotriz'
    descripcion TEXT,
    activo      BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_rubros_updated_at
    BEFORE UPDATE ON rubros
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE rubros IS 'Sectores de negocio soportados por la plataforma';

-- ---------------------------------------------------------------------------
-- 3. PLANES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS planes (
    id_plan             INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre              TEXT        NOT NULL UNIQUE,     -- ej: 'Básico', 'Pro', 'Premium'
    followup_habilitado BOOLEAN     NOT NULL DEFAULT FALSE,
    ia_habilitada       BOOLEAN     NOT NULL DEFAULT TRUE,
    max_leads_mes       INT,                             -- NULL = sin límite
    max_mensajes_mes    INT,
    max_items           INT,
    max_kb_docs         INT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_planes_updated_at
    BEFORE UPDATE ON planes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE planes IS 'Planes de suscripción disponibles para empresas';

-- ---------------------------------------------------------------------------
-- 4. EMPRESAS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS empresas (
    id_empresa       INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre           TEXT        NOT NULL,
    id_rubro         INT         REFERENCES rubros(id_rubro) ON DELETE RESTRICT,
    id_plan          INT         REFERENCES planes(id_plan)  ON DELETE RESTRICT,
    permite_followup BOOLEAN     NOT NULL DEFAULT FALSE,
    activa           BOOLEAN     NOT NULL DEFAULT TRUE,
    timezone         TEXT        NOT NULL DEFAULT 'America/Argentina/Buenos_Aires',
    -- Opcional: slug único para identificar la empresa en URLs/API
    slug             TEXT        UNIQUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_empresas_rubro ON empresas(id_rubro);
CREATE INDEX IF NOT EXISTS idx_empresas_plan  ON empresas(id_plan);

CREATE TRIGGER trg_empresas_updated_at
    BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE  empresas           IS 'Clientes/tenants de la plataforma';
COMMENT ON COLUMN empresas.slug      IS 'Identificador único amigable, opcional';
COMMENT ON COLUMN empresas.timezone  IS 'Zona horaria para scheduling de followups';

-- ---------------------------------------------------------------------------
-- 5. ITEMS  (catálogo multirubro)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS items (
    id_item          UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_empresa       INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    id_rubro         INT         NOT NULL REFERENCES rubros(id_rubro)     ON DELETE RESTRICT,
    tipo             TEXT        NOT NULL,               -- 'inmueble' | 'auto' | 'servicio' | etc.
    categoria        TEXT,
    titulo           TEXT        NOT NULL,
    descripcion      TEXT,
    descripcion_corta TEXT,
    precio           NUMERIC,
    moneda           TEXT,
    activo           BOOLEAN     NOT NULL DEFAULT TRUE,
    destacado        BOOLEAN     NOT NULL DEFAULT FALSE,
    atributos        JSONB       NOT NULL DEFAULT '{}'::JSONB,  -- atributos dinámicos por rubro
    media            JSONB       NOT NULL DEFAULT '{}'::JSONB,  -- fotos, videos, etc.
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_items_empresa_activo  ON items(id_empresa, activo);
CREATE INDEX IF NOT EXISTS idx_items_empresa_rubro   ON items(id_empresa, id_rubro);
CREATE INDEX IF NOT EXISTS idx_items_destacado       ON items(id_empresa, destacado) WHERE destacado = TRUE;
CREATE INDEX IF NOT EXISTS idx_items_atributos_gin   ON items USING GIN(atributos);
CREATE INDEX IF NOT EXISTS idx_items_media_gin       ON items USING GIN(media);
-- Full-text search sobre título + descripción
CREATE INDEX IF NOT EXISTS idx_items_fts ON items
    USING GIN(to_tsvector('spanish', titulo || ' ' || COALESCE(descripcion, '')));

CREATE TRIGGER trg_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE  items           IS 'Catálogo unificado de productos/propiedades/servicios por empresa';
COMMENT ON COLUMN items.atributos IS 'Atributos dinámicos según rubro (ej: dormitorios, km, potencia)';
COMMENT ON COLUMN items.media     IS 'URLs de fotos/videos estructuradas como JSON';

-- ---------------------------------------------------------------------------
-- 6. KB_DOCUMENTS  (knowledge base)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kb_documents (
    id_documento     UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_empresa       INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    id_rubro         INT         NOT NULL REFERENCES rubros(id_rubro)     ON DELETE RESTRICT,
    titulo           TEXT        NOT NULL,
    contenido_texto  TEXT,                               -- NULL si se usa storage_url
    storage_url      TEXT,                               -- NULL si se usa contenido_texto
    metadata         JSONB       NOT NULL DEFAULT '{}'::JSONB,
    activo           BOOLEAN     NOT NULL DEFAULT TRUE,
    version          INT         NOT NULL DEFAULT 1,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_kb_content CHECK (
        contenido_texto IS NOT NULL OR storage_url IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_kb_docs_empresa_rubro ON kb_documents(id_empresa, id_rubro, activo);
CREATE INDEX IF NOT EXISTS idx_kb_docs_fts ON kb_documents
    USING GIN(to_tsvector('spanish', titulo || ' ' || COALESCE(contenido_texto, '')));

CREATE TRIGGER trg_kb_documents_updated_at
    BEFORE UPDATE ON kb_documents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE  kb_documents                IS 'Documentos de conocimiento por empresa (FAQs, manuales, políticas)';
COMMENT ON COLUMN kb_documents.contenido_texto IS 'Texto embebido directamente';
COMMENT ON COLUMN kb_documents.storage_url     IS 'URL a archivo en storage externo (S3, Cloudinary, etc.)';

-- ---------------------------------------------------------------------------
-- 7. KB_CHUNKS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kb_chunks (
    id_chunk     UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_documento UUID        NOT NULL REFERENCES kb_documents(id_documento) ON DELETE CASCADE,
    orden        INT         NOT NULL,
    chunk_texto  TEXT        NOT NULL,
    metadata     JSONB       NOT NULL DEFAULT '{}'::JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_kb_chunks_orden   CHECK (orden >= 0),
    CONSTRAINT uq_kb_chunks_doc_orden UNIQUE (id_documento, orden)
);

CREATE INDEX IF NOT EXISTS idx_kb_chunks_documento ON kb_chunks(id_documento);

COMMENT ON TABLE kb_chunks IS 'Fragmentos indexables de un kb_document (para RAG / embeddings futuros)';

-- ---------------------------------------------------------------------------
-- 8. RUBRO_SCHEMA
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rubro_schema (
    id_rubro         INT         NOT NULL PRIMARY KEY REFERENCES rubros(id_rubro) ON DELETE RESTRICT,
    search_mode      TEXT        NOT NULL,               -- 'items_structured' | 'kb_text' | 'mixed'
    required_keys    JSONB       NOT NULL DEFAULT '[]'::JSONB,
    facet_keys       JSONB       NOT NULL DEFAULT '[]'::JSONB,
    validation_rules JSONB       NOT NULL DEFAULT '{}'::JSONB,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_rubro_schema_search_mode
        CHECK (search_mode IN ('items_structured', 'kb_text', 'mixed'))
);

COMMENT ON TABLE  rubro_schema            IS 'Define cómo el agente busca e interpreta datos para cada rubro';
COMMENT ON COLUMN rubro_schema.search_mode IS 'items_structured=busca en items, kb_text=busca en KB, mixed=ambos';

-- ---------------------------------------------------------------------------
-- 9. RUBRO_PROMPTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rubro_prompts (
    id_prompt      INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rubro       INT         NOT NULL REFERENCES rubros(id_rubro) ON DELETE RESTRICT,
    system_prompt  TEXT        NOT NULL,
    style_prompt   TEXT,
    tooling_prompt TEXT,
    version        INT         NOT NULL DEFAULT 1,
    activo         BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_rubro_prompts_version CHECK (version >= 1),
    CONSTRAINT uq_rubro_version         UNIQUE (id_rubro, version)
);

CREATE INDEX IF NOT EXISTS idx_rubro_prompts_activo ON rubro_prompts(id_rubro, activo);

COMMENT ON TABLE rubro_prompts IS 'Prompts versionados del sistema por rubro';

-- ---------------------------------------------------------------------------
-- 10. EMPRESA_PROMPT_OVERRIDES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS empresa_prompt_overrides (
    id_override  INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_empresa   INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    prompt_extra TEXT,
    brand_voice  TEXT,
    activo       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Solo puede haber 1 override activo por empresa
CREATE UNIQUE INDEX IF NOT EXISTS uq_empresa_override_activo
    ON empresa_prompt_overrides(id_empresa)
    WHERE activo = TRUE;

CREATE TRIGGER trg_empresa_overrides_updated_at
    BEFORE UPDATE ON empresa_prompt_overrides
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE empresa_prompt_overrides IS 'Personalización del prompt a nivel empresa (brand voice, instrucciones extras)';

-- ---------------------------------------------------------------------------
-- 11. LEADS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leads (
    id_lead    INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_empresa INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    nombre     TEXT,
    telefono   TEXT,
    email      TEXT,
    canal      TEXT,                                     -- 'web' | 'whatsapp' | 'instagram' | etc.
    estado     TEXT        NOT NULL DEFAULT 'nuevo',     -- 'nuevo' | 'en_proceso' | 'cerrado'
    metadata   JSONB       NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_empresa_fecha  ON leads(id_empresa, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_empresa_estado ON leads(id_empresa, estado);

CREATE TRIGGER trg_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE leads IS 'Contactos/prospectos captados por el agente';

-- ---------------------------------------------------------------------------
-- 12. CONVERSACIONES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversaciones (
    id_conversacion INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lead         INT         NOT NULL REFERENCES leads(id_lead)       ON DELETE CASCADE,
    id_empresa      INT         NOT NULL REFERENCES empresas(id_empresa)  ON DELETE CASCADE,
    canal           TEXT        NOT NULL,
    inicio          TIMESTAMPTZ,
    fin             TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_empresa_fecha ON conversaciones(id_empresa, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_lead_fecha    ON conversaciones(id_lead,    created_at DESC);

CREATE TRIGGER trg_conversaciones_updated_at
    BEFORE UPDATE ON conversaciones
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE conversaciones IS 'Sesiones de chat entre un lead y el agente';

-- ---------------------------------------------------------------------------
-- 13. MENSAJES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mensajes (
    id_mensaje      INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_conversacion INT         NOT NULL REFERENCES conversaciones(id_conversacion) ON DELETE CASCADE,
    emisor          TEXT        NOT NULL,                -- 'user' | 'bot' | 'system'
    mensaje         TEXT        NOT NULL,
    raw_payload     JSONB       NOT NULL DEFAULT '{}'::JSONB,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_mensajes_emisor CHECK (emisor IN ('user', 'bot', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_mensajes_conv_ts ON mensajes(id_conversacion, timestamp);

COMMENT ON TABLE  mensajes             IS 'Historial de mensajes de cada conversación';
COMMENT ON COLUMN mensajes.raw_payload IS 'Payload original del canal (WhatsApp, web, etc.)';

-- ---------------------------------------------------------------------------
-- 14. FOLLOWUPS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS followups (
    id_followup      INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lead          INT         NOT NULL REFERENCES leads(id_lead)              ON DELETE CASCADE,
    id_conversacion  INT         REFERENCES conversaciones(id_conversacion)       ON DELETE SET NULL,
    tipo             TEXT        NOT NULL,               -- 'recordatorio' | 'encuesta' | etc.
    estado           TEXT        NOT NULL DEFAULT 'pendiente',
    fecha_programada TIMESTAMPTZ NOT NULL,
    fecha_ejecucion  TIMESTAMPTZ,
    payload          JSONB       NOT NULL DEFAULT '{}'::JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_followups_estado
        CHECK (estado IN ('pendiente', 'enviado', 'cancelado', 'fallido'))
);

-- Índice parcial: solo followups pendientes (los que hay que procesar)
CREATE INDEX IF NOT EXISTS idx_followups_pendientes
    ON followups(fecha_programada)
    WHERE estado = 'pendiente';

CREATE INDEX IF NOT EXISTS idx_followups_lead ON followups(id_lead, created_at DESC);

CREATE TRIGGER trg_followups_updated_at
    BEFORE UPDATE ON followups
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE followups IS 'Acciones programadas de seguimiento sobre un lead';

-- ---------------------------------------------------------------------------
-- 15. CONTEXTOS_CONVERSACION
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contextos_conversacion (
    id_contexto     INT         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_conversacion INT         NOT NULL UNIQUE REFERENCES conversaciones(id_conversacion) ON DELETE CASCADE,
    resumen_contexto TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE contextos_conversacion IS 'Resumen/contexto acumulado de cada conversación (para memoria del agente)';

-- =============================================================================
-- FIN DEL SCRIPT
-- =============================================================================