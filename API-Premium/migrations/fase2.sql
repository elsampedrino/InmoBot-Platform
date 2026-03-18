-- =============================================================================
-- Migración Fase 2 — API Premium InmoBot
-- Ejecutar contra la base de datos antes de levantar la Fase 2.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. session_id en conversaciones
-- Necesario para recuperar una conversación activa por canal + empresa.
-- ---------------------------------------------------------------------------
ALTER TABLE conversaciones
    ADD COLUMN IF NOT EXISTS session_id TEXT;

CREATE INDEX IF NOT EXISTS idx_conv_session_id
    ON conversaciones(id_empresa, session_id)
    WHERE session_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 2. Asegurar estado_json en contextos_conversacion
-- (Ya debería estar si se aplicó la corrección acordada en Fase 1)
-- ---------------------------------------------------------------------------
ALTER TABLE contextos_conversacion
    ADD COLUMN IF NOT EXISTS estado_json JSONB;

-- ---------------------------------------------------------------------------
-- FIN
-- =============================================================================
