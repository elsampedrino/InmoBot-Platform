-- migration_rubro_slug.sql
-- Agrega columna slug a la tabla rubros (para routing multi-contexto)
-- Ejecutar una sola vez en la DB de Render

ALTER TABLE rubros ADD COLUMN IF NOT EXISTS slug TEXT UNIQUE;

-- El seed_saas_inmobot.py se encarga de setear los slugs:
--   id_rubro=1 → 'inmobiliaria_demo'
--   id_rubro=nuevo → 'saas_inmobot'
-- Pero si querés setearlos manualmente:
-- UPDATE rubros SET slug = 'inmobiliaria_demo' WHERE id_rubro = 1;
