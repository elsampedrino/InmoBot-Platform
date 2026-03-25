-- =============================================================================
-- Migración Fase 3 — Campo servicios en empresas
-- Controla qué servicios tiene contratados cada empresa.
-- Separado de config (cómo funciona) y de plan (qué límites tiene).
-- =============================================================================

ALTER TABLE empresas
    ADD COLUMN IF NOT EXISTS servicios JSONB NOT NULL DEFAULT '{"bot": true}';

COMMENT ON COLUMN empresas.servicios IS
    'Servicios contratados por la empresa. Ej: {"bot": true, "landing": true}. '
    'Controla visibilidad de funcionalidades en el panel y validaciones en backend.';

-- Actualizar empresa piloto Cristian con ambos servicios activos
UPDATE empresas
SET servicios = '{"bot": true, "landing": true}'
WHERE slug = 'cristian-inmob';

-- =============================================================================
-- FIN
-- =============================================================================