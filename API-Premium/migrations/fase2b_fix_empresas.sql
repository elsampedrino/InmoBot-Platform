-- =============================================================================
-- Migración Fase 2b — Seed de datos para pruebas
-- El rubro se asigna via empresa_rubros (es_default=true), NO en empresas.
-- =============================================================================

-- Seed: Rubro inmobiliaria
INSERT INTO rubros (nombre, descripcion, activo)
VALUES ('Inmobiliaria', 'Agencias y profesionales inmobiliarios', true)
ON CONFLICT (nombre) DO NOTHING;

-- Seed: Empresa BBR (verificar que el slug no exista antes)
INSERT INTO empresas (nombre, id_plan, slug, activa, timezone, permite_followup)
VALUES (
    'BBR Grupo Inmobiliario',
    NULL,
    'bbr-inmobiliaria',
    true,
    'America/Argentina/Buenos_Aires',
    false
)
ON CONFLICT (slug) DO NOTHING;

-- Seed: Asignar rubro inmobiliaria a BBR como default
INSERT INTO empresa_rubros (id_empresa, id_rubro, activo, es_default)
VALUES (
    (SELECT id_empresa FROM empresas WHERE slug = 'bbr-inmobiliaria'),
    (SELECT id_rubro  FROM rubros   WHERE nombre = 'Inmobiliaria'),
    true,
    true
)
ON CONFLICT (id_empresa, id_rubro) DO UPDATE SET es_default = true, activo = true;

-- Seed: Prompt del rubro inmobiliaria
INSERT INTO rubro_prompts (id_rubro, system_prompt, style_prompt, version, activo)
VALUES (
    (SELECT id_rubro FROM rubros WHERE nombre = 'Inmobiliaria'),
    'Sos un asistente virtual inmobiliario amigable y profesional. '
    'Tu objetivo es ayudar al usuario a encontrar la propiedad ideal '
    'respondiendo sus consultas de forma clara, concisa y empática.',
    'Usá un tono cercano y profesional. Respondé en español rioplatense.',
    1,
    true
)
ON CONFLICT (id_rubro, version) DO NOTHING;

-- Seed: Schema del rubro
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