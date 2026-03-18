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
-- 3. id_lead nullable en conversaciones
-- La conversación se crea al primer mensaje; el lead se vincula después.
-- Si la columna fue creada NOT NULL, eliminar la restricción.
-- ---------------------------------------------------------------------------
ALTER TABLE conversaciones
    ALTER COLUMN id_lead DROP NOT NULL;

-- =============================================================================
-- SEED DE DATOS MÍNIMOS PARA PRUEBAS
-- Adaptar nombre/slug antes de correr en producción.
-- =============================================================================

-- Rubro base: Inmobiliaria
INSERT INTO rubros (nombre, descripcion, activo)
VALUES ('Inmobiliaria', 'Agencias y profesionales inmobiliarios', true)
ON CONFLICT (nombre) DO NOTHING;

-- Empresa de prueba: BBR Grupo Inmobiliario
INSERT INTO empresas (nombre, id_rubro, slug, activa, timezone, permite_followup)
VALUES (
    'BBR Grupo Inmobiliario',
    (SELECT id_rubro FROM rubros WHERE nombre = 'Inmobiliaria'),
    'bbr-inmobiliaria',
    true,
    'America/Argentina/Buenos_Aires',
    false
)
ON CONFLICT (slug) DO NOTHING;

-- Prompt del rubro inmobiliaria (versión 1)
INSERT INTO rubro_prompts (id_rubro, system_prompt, style_prompt, version, activo)
VALUES (
    (SELECT id_rubro FROM rubros WHERE nombre = 'Inmobiliaria'),
    'Sos un asistente virtual inmobiliario amigable y profesional. '
    'Tu objetivo es ayudar al usuario a encontrar la propiedad ideal '
    'respondiendo sus consultas de forma clara, concisa y empática. '
    'Cuando el usuario muestra interés concreto, ofrecé conectarlo con un asesor.',
    'Usá un tono cercano y profesional. Evitá respuestas largas. '
    'Respondé siempre en español rioplatense.',
    1,
    true
)
ON CONFLICT (id_rubro, version) DO NOTHING;

-- Schema del rubro inmobiliaria
INSERT INTO rubro_schema (id_rubro, search_mode, required_keys, facet_keys, validation_rules)
VALUES (
    (SELECT id_rubro FROM rubros WHERE nombre = 'Inmobiliaria'),
    'items_structured',
    '["tipo", "titulo", "precio", "moneda"]',
    '["tipo", "operacion", "zona", "dormitorios", "precio"]',
    '{}'
)
ON CONFLICT (id_rubro) DO NOTHING;

-- =============================================================================
-- FIN
-- =============================================================================