"""
test_demo.py — 4 casos de prueba para la demo con Yamila.
Ejecutar: cd API-Premium && venv/Scripts/python test_demo.py
"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.api_models import ChatMessageRequest
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.property_resolver import resolve_property
from app.services.tenant_resolver import TenantResolver

DATABASE_URL = (
    "postgresql+asyncpg://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI"
    "@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"
)

EMPRESA = "houghton"

CASOS = [
    {
        "nombre": "PROP-001 — Depto Palermo (disponibilidad + expensas)",
        "url":    "https://www.pablohoughton.com.ar/p/7837181-Departamento-en-Venta-en-Palermo",
        "pregunta": "Esta disponible? Cuanto son las expensas y el ABL?",
        "session": "demo_test_001",
    },
    {
        "nombre": "PROP-005 — Depto Caballito (apto profesional + orientacion)",
        "url":    "https://www.pablohoughton.com.ar/p/5023783",
        "pregunta": "Es apto profesional? Que orientacion tiene?",
        "session": "demo_test_005",
    },
    {
        "nombre": "PROP-010 — Casa Florida (situacion + ABL + cocheras)",
        "url":    "https://www.pablohoughton.com.ar/p/4966210",
        "pregunta": "Esta disponible para visitar? Cuanto es el ABL? Cuantas cocheras tiene?",
        "session": "demo_test_010",
    },
    {
        "nombre": "PROP-015 — Depto Nuñez en construccion (entrega + amenities + apto prof)",
        "url":    "https://www.pablohoughton.com.ar/p/7522782",
        "pregunta": "Cuando es la entrega? Tiene SUM y solarium? Es apto profesional?",
        "session": "demo_test_015",
    },
    {
        "nombre": "PROP-025 — Local Palermo Hollywood (apto prof + rubros + 4 vientos)",
        "url":    "https://www.pablohoughton.com.ar/p/2389275",
        "pregunta": "Es apto profesional? Que rubros estan habilitados? Tiene tiraje a 4 vientos?",
        "session": "demo_test_025",
    },
]


async def run_caso(Session, caso: dict) -> None:
    sid = caso["session"]

    # Reset conversacion previa
    async with Session() as s:
        await s.execute(
            text("UPDATE conversaciones SET fin = NOW() WHERE session_id = :sid AND fin IS NULL"),
            {"sid": sid},
        )
        await s.commit()

    # Turno 1: URL silenciosa → guarda propiedad en estado
    async with Session() as s:
        tenant = await TenantResolver(s).resolve(EMPRESA)
        prop = await resolve_property(caso["url"], tenant.id_empresa, s)
        if not prop:
            print(f"  [ERROR] No se encontro la propiedad para URL: {caso['url']}")
            return

        silent_req = ChatMessageRequest(
            empresa_slug=EMPRESA, canal="whatsapp",
            session_id=sid, mensaje="__property_link__",
            metadata={"property_context": prop, "silent": True},
        )
        await ChatOrchestrator(s).handle_message(silent_req)
        await s.commit()

    # Turno 2: pregunta especifica
    async with Session() as s:
        req = ChatMessageRequest(
            empresa_slug=EMPRESA, canal="whatsapp",
            session_id=sid, mensaje=caso["pregunta"],
            metadata={},
        )
        resp = await ChatOrchestrator(s).handle_message(req)
        await s.commit()

    respuesta = resp.respuesta.encode("ascii", errors="replace").decode("ascii")
    print(f"\n  Pregunta: {caso['pregunta']}")
    print(f"  Respuesta:\n{respuesta}\n")
    print("  " + "-" * 60)


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    for i, caso in enumerate(CASOS, 1):
        print(f"\n{'='*65}")
        print(f"  CASO {i}: {caso['nombre']}")
        print(f"{'='*65}")
        await run_caso(Session, caso)

    await engine.dispose()
    print("\n[DONE] 4 casos ejecutados.")


if __name__ == "__main__":
    asyncio.run(main())
