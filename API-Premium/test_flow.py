import asyncio, sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.api_models import ChatMessageRequest
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.property_resolver import resolve_property
from app.services.tenant_resolver import TenantResolver
from sqlalchemy import text

DATABASE_URL = (
    "postgresql+asyncpg://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI"
    "@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"
)
SESSION_ID = "test_directo_999"
EMPRESA    = "houghton"
URL_MSG    = "https://www.pablohoughton.com.ar/p/7837181-Departamento-en-Venta-en-Palermo-Uriarte-al-2200"


async def run():
    engine  = create_async_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Reset
    async with Session() as s:
        await s.execute(text(
            "UPDATE conversaciones SET fin = NOW() WHERE session_id = :sid AND fin IS NULL"
        ), {"sid": SESSION_ID})
        await s.commit()

    # Turno 1: URL silenciosa
    async with Session() as s:
        tenant = await TenantResolver(s).resolve(EMPRESA)
        prop   = await resolve_property(URL_MSG, tenant.id_empresa, s)
        print(f"[Resolver] {prop['external_id']} - {prop['titulo'][:40]}")

        silent_req = ChatMessageRequest(
            empresa_slug=EMPRESA, canal="whatsapp",
            session_id=SESSION_ID, mensaje="__property_link__",
            metadata={"property_context": prop, "silent": True},
        )
        await ChatOrchestrator(s).handle_message(silent_req)
        await s.commit()
        print("[Turno 1] Guardado silencioso OK + commit")

    # Verificar estado en DB
    async with Session() as s:
        r = await s.execute(text("""
            SELECT cc.estado_json
            FROM contextos_conversacion cc
            JOIN conversaciones c ON c.id_conversacion = cc.id_conversacion
            WHERE c.session_id = :sid AND c.fin IS NULL
            ORDER BY cc.updated_at DESC LIMIT 1
        """), {"sid": SESSION_ID})
        row = r.fetchone()
        if row:
            estado = row[0]
            print(f"[Estado DB] ultimo_item_referenciado = {estado.get('ultimo_item_referenciado')}")
            print(f"[Estado DB] items_recientes = {estado.get('items_recientes')}")
        else:
            print("[PROBLEMA] No hay estado en DB!")

    # Turno 2: pregunta
    async with Session() as s:
        req2 = ChatMessageRequest(
            empresa_slug=EMPRESA, canal="whatsapp",
            session_id=SESSION_ID,
            mensaje="Esta disponible? Cuanto son las expensas?",
            metadata={},
        )
        resp = await ChatOrchestrator(s).handle_message(req2)
        print(f"\n[Turno 2 respuesta]\n{resp.respuesta}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
