"""
migrate_premium_tables.py
Crea las tablas premium_chat_logs, premium_chat_log_items,
premium_conversion_logs y premium_conversion_log_items si no existen.

Uso:
    python scripts/migrate_premium_tables.py [--dry-run]
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from app.core.config import settings

DDL_DROP = """
DROP TABLE IF EXISTS premium_conversion_log_items CASCADE;
DROP TABLE IF EXISTS premium_conversion_logs CASCADE;
DROP TABLE IF EXISTS premium_chat_log_items CASCADE;
DROP TABLE IF EXISTS premium_chat_logs CASCADE;
"""

DDL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- premium_chat_logs
CREATE TABLE IF NOT EXISTS premium_chat_logs (
    id_log                UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_empresa            INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    id_conversacion       INT         REFERENCES conversaciones(id_conversacion) ON DELETE SET NULL,
    session_id            TEXT,
    canal                 TEXT,
    route_elegida         TEXT,
    intent_detectada      TEXT,
    hubo_fallback_ia      BOOLEAN     NOT NULL DEFAULT FALSE,
    confidence_score      FLOAT,
    model_usado           TEXT,
    tokens_input          INT,
    tokens_output         INT,
    response_time_ms      INT,
    items_mostrados_count INT         NOT NULL DEFAULT 0,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pcl_empresa_fecha
    ON premium_chat_logs(id_empresa, created_at DESC);

-- premium_chat_log_items
CREATE TABLE IF NOT EXISTS premium_chat_log_items (
    id         UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_log     UUID NOT NULL REFERENCES premium_chat_logs(id_log) ON DELETE CASCADE,
    id_item    UUID NOT NULL REFERENCES items(id_item) ON DELETE CASCADE,
    posicion   INT  NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pcli_log
    ON premium_chat_log_items(id_log);

-- premium_conversion_logs
CREATE TABLE IF NOT EXISTS premium_conversion_logs (
    id_conversion   UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_empresa      INT         NOT NULL REFERENCES empresas(id_empresa) ON DELETE CASCADE,
    id_conversacion INT         REFERENCES conversaciones(id_conversacion) ON DELETE SET NULL,
    id_lead         INT         REFERENCES leads(id_lead) ON DELETE SET NULL,
    evento          TEXT        NOT NULL,
    route           TEXT,
    metadata        JSONB       NOT NULL DEFAULT '{}'::JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pcvl_empresa_fecha
    ON premium_conversion_logs(id_empresa, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pcvl_empresa_evento
    ON premium_conversion_logs(id_empresa, evento);

-- premium_conversion_log_items
CREATE TABLE IF NOT EXISTS premium_conversion_log_items (
    id            UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    id_conversion UUID NOT NULL REFERENCES premium_conversion_logs(id_conversion) ON DELETE CASCADE,
    id_item       UUID NOT NULL REFERENCES items(id_item) ON DELETE CASCADE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pcvli_conversion
    ON premium_conversion_log_items(id_conversion);
"""

async def main(dry_run: bool) -> None:
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)
    try:
        if dry_run:
            print("[DRY-RUN] SQL que se ejecutaria:")
            print(DDL_DROP)
            print(DDL)
            return

        # Paso 1: Drop tablas con schema viejo
        print("--- Eliminando tablas con schema antiguo ---")
        drop_stmts = [s.strip() for s in DDL_DROP.split(";") if s.strip()]
        for stmt in drop_stmts:
            await conn.execute(stmt)
            print(f"OK: {stmt[:80]}")

        # Paso 2: Crear con nuevo schema
        print("\n--- Creando tablas con nuevo schema ---")
        statements = [s.strip() for s in DDL.split(";") if s.strip()]
        for stmt in statements:
            try:
                await conn.execute(stmt)
                first_line = stmt.splitlines()[0][:80]
                print(f"OK: {first_line}")
            except Exception as e:
                print(f"ERROR en: {stmt[:80]}\n  -> {e}")
                raise

        print("\nMigracion completada.")

        # Verificar
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name LIKE 'premium_%'
            ORDER BY table_name
        """)
        print("Tablas premium existentes:")
        for t in tables:
            print(f"  - {t['table_name']}")

        cols = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN (
                'premium_chat_logs', 'premium_chat_log_items',
                'premium_conversion_logs', 'premium_conversion_log_items'
            )
            ORDER BY table_name, ordinal_position
        """)
        print("\nColumnas:")
        cur_table = None
        for c in cols:
            if c['table_name'] != cur_table:
                cur_table = c['table_name']
                print(f"  [{cur_table}]")
            print(f"    {c['column_name']:30s} {c['data_type']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run))
