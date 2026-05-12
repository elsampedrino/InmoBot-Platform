-- facebook_migration.sql
-- Ejecutar contra la DB de producción antes de desplegar la funcionalidad Facebook.
-- Requiere que instagram_migration.sql ya haya sido ejecutado.

-- 1. Agregar page_id a la tabla de config de IG/FB
ALTER TABLE empresa_instagram_config
    ADD COLUMN IF NOT EXISTS page_id TEXT;

-- 2. Tabla de registro de publicaciones en Facebook
CREATE TABLE IF NOT EXISTS facebook_posts (
    id               SERIAL      PRIMARY KEY,
    id_empresa       INTEGER     NOT NULL REFERENCES empresas(id_empresa)       ON DELETE CASCADE,
    id_item          UUID        NOT NULL REFERENCES items(id_item)             ON DELETE CASCADE,
    id_usuario       INTEGER              REFERENCES usuarios_admin(id_usuario) ON DELETE SET NULL,
    caption          TEXT        NOT NULL,
    image_url        TEXT        NOT NULL,
    status           TEXT        NOT NULL DEFAULT 'pending',  -- pending | published | error
    provider_post_id TEXT,                                    -- post_id retornado por Facebook Graph API
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_fb_posts_empresa ON facebook_posts(id_empresa, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fb_posts_item    ON facebook_posts(id_item);
