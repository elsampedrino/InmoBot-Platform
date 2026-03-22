"""
check_db_schema.py - verifica el esquema actual de las tablas premium_* y conversaciones.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from app.core.config import settings


async def main() -> None:
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)
    try:
        # Tablas existentes relevantes
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN (
                'premium_chat_logs', 'premium_chat_log_items',
                'premium_conversion_logs', 'premium_conversion_log_items',
                'conversaciones', 'leads'
              )
            ORDER BY table_name
        """)
        existing = {t['table_name'] for t in tables}
        print("Tablas existentes:", sorted(existing))
        print()

        # Columnas de cada tabla existente
        for tbl in sorted(existing):
            cols = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, tbl)
            print(f"[{tbl}]")
            for c in cols:
                print(f"  {c['column_name']:35s} {c['data_type']:20s} nullable={c['is_nullable']}")
            print()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
