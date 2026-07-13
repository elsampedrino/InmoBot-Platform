import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        'postgresql://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl',
        ssl='require'
    )
    rows = await conn.fetch("SELECT id_empresa, slug, nombre FROM empresas ORDER BY id_empresa")
    for r in rows:
        print(f"  id={r['id_empresa']} slug={r['slug']} nombre={r['nombre']}")
    await conn.close()

asyncio.run(main())
