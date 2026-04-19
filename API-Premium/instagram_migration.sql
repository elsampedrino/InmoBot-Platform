-- instagram_migration.sql
-- Ejecutar contra la DB de producción antes de desplegar la funcionalidad Instagram.

CREATE TABLE IF NOT EXISTS empresa_instagram_config (
    id_empresa       INTEGER     PRIMARY KEY REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    ig_user_id       TEXT        NOT NULL,
    access_token     TEXT        NOT NULL,   -- token sensible, nunca exponer en API responses
    token_expires_at TIMESTAMPTZ,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS instagram_posts (
    id               SERIAL      PRIMARY KEY,
    id_empresa       INTEGER     NOT NULL REFERENCES empresas(id_empresa)       ON DELETE CASCADE,
    id_item          UUID        NOT NULL REFERENCES items(id_item)             ON DELETE CASCADE,
    id_usuario       INTEGER              REFERENCES usuarios_admin(id_usuario) ON DELETE SET NULL,
    caption          TEXT        NOT NULL,
    image_url        TEXT        NOT NULL,
    status           TEXT        NOT NULL DEFAULT 'pending',  -- pending | published | error
    provider_post_id TEXT,                                    -- ID retornado por Instagram Graph API
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ig_posts_empresa ON instagram_posts(id_empresa, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ig_posts_item    ON instagram_posts(id_item);
