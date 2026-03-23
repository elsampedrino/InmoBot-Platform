"""
smoke_test_render.py — Smoke test de post-deploy contra la API Premium en Render.

Verifica que el servicio esté operativo con el mínimo de requests necesarios
para confirmar la salida a piloto. No reemplaza el E2E completo.

Uso:
    python scripts/smoke_test_render.py --url https://inmobot-premium-api.onrender.com --slug cristian-inmob

Requiere httpx:
    pip install httpx
"""
import io
import sys
# Forzar UTF-8 en stdout (necesario en Windows con cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone

import httpx

# ─── Defaults ────────────────────────────────────────────────────────────────

DEFAULT_URL  = "https://inmobot-premium-api.onrender.com"
DEFAULT_SLUG = "cristian-inmob"
TIMEOUT      = 60.0   # segundos — el primer request puede tardar más (cold start)

# ─── Helpers ─────────────────────────────────────────────────────────────────

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

passed = failed = 0


def ok(label: str, detail: str = "") -> None:
    global passed
    passed += 1
    suffix = f"  ({detail})" if detail else ""
    print(f"  {PASS} {label}{suffix}")


def fail(label: str, detail: str = "") -> None:
    global failed
    failed += 1
    suffix = f"  ({detail})" if detail else ""
    print(f"  {FAIL} {label}{suffix}")


def check(label: str, cond: bool, detail: str = "") -> bool:
    if cond:
        ok(label, detail)
    else:
        fail(label, detail)
    return cond


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─── Tests ───────────────────────────────────────────────────────────────────

async def test_health(client: httpx.AsyncClient, base_url: str) -> bool:
    section("1. HEALTHCHECK — GET /health")
    try:
        r = await client.get(f"{base_url}/health", timeout=TIMEOUT)
        print(f"  HTTP {r.status_code}")
        if not check("status 200", r.status_code == 200, f"got {r.status_code}"):
            return False
        data = r.json()
        check("status == 'ok'", data.get("status") == "ok", repr(data.get("status")))
        check("db == 'ok'", data.get("db") == "ok",
              f"got {data.get('db')!r}  ← si falla: revisar DATABASE_URL")
        print(f"  version: {data.get('version')!r}")
        return data.get("db") == "ok"
    except Exception as e:
        fail("healthcheck", str(e))
        return False


async def test_saludo(client: httpx.AsyncClient, endpoint: str, session_id: str) -> bool:
    section("2. SALUDO — contrato legacy basico")
    payload = {
        "message": "Hola",
        "sessionId": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": "bbr",
    }
    try:
        r = await client.post(endpoint, json=payload, timeout=TIMEOUT)
        print(f"  HTTP {r.status_code}")
        if not check("status 200", r.status_code == 200, f"got {r.status_code}"):
            print(f"  body: {r.text[:300]}")
            return False
        data = r.json()
        ok_response = check("success == True", data.get("success") is True)
        ok_response &= check("response no vacio",
                             bool(data.get("response")), f"len={len(data.get('response',''))}")
        ok_response &= check("sessionId == enviado", data.get("sessionId") == session_id)
        props_raw = data.get("propiedades_detalladas")
        ok_response &= check("propiedades_detalladas es lista",
                             isinstance(props_raw, list), type(props_raw).__name__)
        ok_response &= check("leads es bool", isinstance(data.get("leads"), bool),
                             type(data.get("leads")).__name__)
        ok_response &= check("timestamp presente", bool(data.get("timestamp")))
        response_preview = (data.get("response") or "")[:80]
        print(f"  response: {response_preview!r}...")
        return ok_response
    except Exception as e:
        fail("saludo", str(e))
        return False


async def test_busqueda(client: httpx.AsyncClient, endpoint: str, session_id: str) -> bool:
    section("3. BUSQUEDA — propiedades y leads")
    payload = {
        "message": "Busco una casa para comprar",
        "sessionId": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": "bbr",
    }
    try:
        r = await client.post(endpoint, json=payload, timeout=TIMEOUT)
        print(f"  HTTP {r.status_code}")
        if not check("status 200", r.status_code == 200, f"got {r.status_code}"):
            return False
        data = r.json()
        props_raw = data.get("propiedades_detalladas")
        props = props_raw if props_raw is not None else []
        leads = data.get("leads")
        check("propiedades_detalladas es lista", isinstance(props, list))
        check("hay propiedades", len(props) > 0, f"got {len(props)}")
        check("leads == True con propiedades", leads is True,
              f"got {leads!r}  ← widget no mostrara botones si leads !== true")
        check("propiedadesMostradas coherente",
              data.get("propiedadesMostradas") == len(props),
              f"pm={data.get('propiedadesMostradas')} len={len(props)}")
        if props:
            p0 = props[0]
            check("prop[0].id no vacio", bool(p0.get("id")))
            check("prop[0].tipo no vacio", bool(p0.get("tipo")), repr(p0.get("tipo")))
            check("prop[0].operacion no vacia", bool(p0.get("operacion")), repr(p0.get("operacion")))
            print(f"  tipo[0]={p0.get('tipo')!r}  operacion[0]={p0.get('operacion')!r}")
        return True
    except Exception as e:
        fail("busqueda", str(e))
        return False


async def test_lead(client: httpx.AsyncClient, endpoint: str, session_id: str) -> bool:
    section("4. CAPTURA DE LEAD — datos de contacto")
    payload = {
        "message": "me llamo Juan Gomez y mi telefono es 351-555-9999",
        "sessionId": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": "bbr",
    }
    try:
        r = await client.post(endpoint, json=payload, timeout=TIMEOUT)
        print(f"  HTTP {r.status_code}")
        if not check("status 200", r.status_code == 200, f"got {r.status_code}"):
            return False
        data = r.json()
        check("success == True", data.get("success") is True)
        check("response no vacio", bool(data.get("response")))
        response_preview = (data.get("response") or "")[:100]
        print(f"  response: {response_preview!r}...")
        return True
    except Exception as e:
        fail("lead", str(e))
        return False


async def test_invalid_payload(client: httpx.AsyncClient, endpoint: str) -> bool:
    section("5. PAYLOAD INVALIDO — validacion de request")
    try:
        # Sin campo message
        r = await client.post(endpoint, json={"sessionId": "x"}, timeout=10.0)
        check("message faltante -> 422", r.status_code == 422, f"got {r.status_code}")
        # message vacio
        r = await client.post(endpoint, json={"message": "", "sessionId": "x"}, timeout=10.0)
        check("message vacio -> 422", r.status_code == 422, f"got {r.status_code}")
        # slug inexistente
        bad_endpoint = endpoint.replace("/cristian-inmob/", "/slug-que-no-existe/")
        r = await client.post(bad_endpoint, json={"message": "hola", "sessionId": "x"}, timeout=10.0)
        check("slug invalido -> 4xx", r.status_code >= 400, f"got {r.status_code}")
        return True
    except Exception as e:
        fail("invalid_payload", str(e))
        return False


# ─── Main ────────────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test post-deploy InmoBot Premium")
    parser.add_argument("--url",  default=DEFAULT_URL,  help="Base URL de la API en Render")
    parser.add_argument("--slug", default=DEFAULT_SLUG, help="empresa_slug del tenant piloto")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    endpoint = f"{base_url}/webhook/{args.slug}/chat"
    session_id = f"smoke-{int(time.time())}"

    print(f"\nInmoBot Premium — Smoke Test Post-Deploy")
    print(f"  API:      {base_url}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Session:  {session_id}")

    async with httpx.AsyncClient() as client:
        health_ok = await test_health(client, base_url)
        if not health_ok:
            print("\n  ABORT: healthcheck fallido. Verificar deploy y variables de entorno.")
            sys.exit(1)

        await test_saludo(client, endpoint, session_id)
        await test_busqueda(client, endpoint, session_id)
        await test_lead(client, endpoint, session_id)
        await test_invalid_payload(client, endpoint)

    total = passed + failed
    section("RESUMEN")
    status = PASS if failed == 0 else FAIL
    print(f"  {status} {passed}/{total} checks pasados")

    if failed == 0:
        print("\n  Sistema listo para piloto web.")
    else:
        print(f"\n  {failed} check(s) fallidos. Revisar logs en Render antes de habilitar el widget.")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
