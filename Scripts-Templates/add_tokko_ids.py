"""
add_tokko_ids.py — Agrega tokko_id a atributos de todos los items de Houghton.
El ID se extrae de la primera URL de foto (tokkobroker.com/pictures/{ID}_{hash}.jpg)
"""
import asyncio, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "API-Premium"))
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql+asyncpg://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI"
    "@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"
)

async def run():
    data = json.loads(
        (Path(__file__).parent.parent / "Inmob Houghton" / "propiedades_houghton.json")
        .read_text(encoding="utf-8-sig")
    )
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    updated = 0
    async with async_session() as session:
        for prop in data["propiedades"]:
            urls = prop.get("fotos", {}).get("urls") or []
            if not urls:
                continue
            match = re.search(r"/pictures/(\d+)_", urls[0])
            if not match:
                continue
            tokko_id = match.group(1)

            patch = json.dumps({"tokko_id": tokko_id})
            await session.execute(text("""
                UPDATE items
                SET atributos = atributos || CAST(:patch AS jsonb)
                WHERE external_id = :eid
                  AND id_empresa = (SELECT id_empresa FROM empresas WHERE slug = 'houghton')
            """), {"patch": patch, "eid": prop["id"]})
            updated += 1
            print(f"[OK] {prop['id']} tokko_id={tokko_id}")

        await session.commit()
    await engine.dispose()
    print(f"\n[DONE] {updated} propiedades actualizadas con tokko_id")

if __name__ == "__main__":
    asyncio.run(run())
