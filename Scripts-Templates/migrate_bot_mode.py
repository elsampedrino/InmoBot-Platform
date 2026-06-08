import asyncio
import asyncpg

DB_URL = "postgresql://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"

async def main():
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS bot_mode TEXT NOT NULL DEFAULT 'always_on'")
    await conn.execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS horario_config JSONB DEFAULT NULL")
    rows = await conn.fetch("SELECT id_empresa, nombre, bot_mode FROM empresas ORDER BY id_empresa")
    for r in rows:
        print(f"  {r['id_empresa']} | {r['nombre']:<30} | {r['bot_mode']}")
    await conn.close()
    print("Migration OK")

asyncio.run(main())
