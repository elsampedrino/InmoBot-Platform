-- =============================================================================
-- Migración Fase 3b — Tabla usuarios_admin
-- Usuarios del panel administrativo. Un usuario por empresa para el MVP.
-- =============================================================================

CREATE TABLE IF NOT EXISTS usuarios_admin (
    id_usuario      SERIAL PRIMARY KEY,
    id_empresa      INTEGER NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    nombre          TEXT,
    activo          BOOLEAN NOT NULL DEFAULT true,
    es_superadmin   BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_admin_empresa ON usuarios_admin(id_empresa);

-- =============================================================================
-- FIN — usar scripts/crear_admin.py para crear el primer usuario
-- =============================================================================