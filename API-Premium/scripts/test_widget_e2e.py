"""
test_widget_e2e.py — Validación E2E del endpoint /webhook/{empresa_slug}/chat
contra el contrato legacy que espera el widget.

Simula exactamente lo que hace ChatWidget.jsx:
  - Envía { message, sessionId, timestamp, repo }
  - Lee data.response, data.propiedades_detalladas, data.leads, data.sessionId

Uso:
    python scripts/test_widget_e2e.py [--base-url http://localhost:8001] [--slug cristian-inmob]
"""
import asyncio
import io
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

# Forzar UTF-8 en stdout (necesario en Windows con cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx

# ─── Config ──────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8001"
EMPRESA_SLUG = "cristian-inmob"
SESSION_ID = f"session-{int(time.time())}-test9e2e"
REPO = "bbr"

# ─── Helpers ─────────────────────────────────────────────────────────────────

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

results: list[dict] = []


def check(label: str, cond: bool, detail: str = "") -> bool:
    mark = PASS if cond else FAIL
    msg = f"  {mark} {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    return cond


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def record(scenario: str, passed: int, total: int) -> None:
    results.append({"scenario": scenario, "passed": passed, "total": total})


def widget_request(message: str) -> dict:
    """Construye el body exacto que envía ChatWidget.jsx."""
    return {
        "message": message,
        "sessionId": SESSION_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": REPO,
    }


def validate_base_contract(data: dict) -> tuple[int, int]:
    """
    Valida los campos que el widget SIEMPRE lee del response.
    Retorna (passed, total).
    """
    p = t = 0

    # 1. success debe ser bool True
    t += 1; p += check("success == True (bool)", data.get("success") is True,
                        f"got {data.get('success')!r}")

    # 2. response debe ser string no vacío
    response = data.get("response") or data.get("respuesta_bot", "")
    t += 1; p += check("response es string no vacío", isinstance(response, str) and len(response) > 0,
                        f"len={len(response)}")

    # 3. sessionId debe coincidir con el enviado
    t += 1; p += check("sessionId == enviado", data.get("sessionId") == SESSION_ID,
                        f"got {data.get('sessionId')!r}")

    # 4. propiedades_detalladas o propiedades debe ser lista (nunca null)
    # NOTA: usar 'is None' y no 'or' — una lista vacía [] es válida y falsy en Python
    _props_raw = data.get("propiedades_detalladas")
    props = _props_raw if _props_raw is not None else data.get("propiedades")
    t += 1; p += check("propiedades_detalladas es lista", isinstance(props, list),
                        f"got {type(props).__name__}")

    # 5. leads debe ser bool exacto (el widget usa data.leads === true)
    leads = data.get("leads")
    t += 1; p += check("leads es bool exacto", isinstance(leads, bool),
                        f"got {leads!r} ({type(leads).__name__})")

    # 6. leads coherente con propiedades: True ↔ hay items
    if isinstance(props, list) and isinstance(leads, bool):
        expected_leads = len(props) > 0
        t += 1; p += check("leads coherente con propiedades",
                            leads == expected_leads,
                            f"propiedades={len(props)} leads={leads}")

    # 7. propiedadesMostradas == len(propiedades_detalladas)
    if isinstance(props, list):
        pm = data.get("propiedadesMostradas", -1)
        t += 1; p += check("propiedadesMostradas == len(props)",
                            pm == len(props),
                            f"pm={pm} len={len(props)}")

    # 8. timestamp es ISO string parseable
    ts = data.get("timestamp", "")
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        ts_ok = True
    except Exception:
        ts_ok = False
    t += 1; p += check("timestamp es ISO válido", ts_ok, f"got {ts!r}")

    return p, t


def validate_property_item(prop: dict, idx: int) -> tuple[int, int]:
    """
    Valida un item de propiedades_detalladas contra lo que el widget
    realmente usa (solo propiedades.length importa para botones,
    pero validamos completitud del mapping).
    """
    p = t = 0
    prefix = f"  prop[{idx}]"

    # id — necesario para trazabilidad
    t += 1; p += check(f"{prefix}.id no vacío",
                        bool(prop.get("id")))

    # titulo — útil si se usa en futuras versiones del widget
    t += 1; p += check(f"{prefix}.titulo no vacío",
                        bool(prop.get("titulo")))

    # tipo — mapeado desde ItemCandidate.tipo
    t += 1; p += check(f"{prefix}.tipo no vacío",
                        bool(prop.get("tipo")),
                        f"got {prop.get('tipo')!r}")

    # imagenes es lista (puede estar vacía)
    imgs = prop.get("imagenes", [])
    t += 1; p += check(f"{prefix}.imagenes es lista",
                        isinstance(imgs, list))

    # detalles es lista
    det = prop.get("detalles", [])
    t += 1; p += check(f"{prefix}.detalles es lista",
                        isinstance(det, list))

    # direccion tiene barrio o ciudad
    direccion = prop.get("direccion") or {}
    t += 1; p += check(f"{prefix}.direccion tiene barrio o ciudad",
                        bool(direccion.get("barrio") or direccion.get("ciudad")))

    return p, t


# ─── Escenarios ───────────────────────────────────────────────────────────────

async def test_saludo(client: httpx.AsyncClient) -> None:
    section("1. SALUDO — ¿Hola?")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("Hola, ¿qué podés hacer?"))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        # En saludo no debe haber propiedades
        props = data.get("propiedades_detalladas", [])
        t += 1; p += check("sin propiedades en saludo", len(props) == 0,
                            f"got {len(props)}")
        t += 1; p += check("leads=False en saludo", data.get("leads") is False)
        print(f"  response[:100]: {data.get('response','')[:100]!r}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}: {r.text[:200]}")
    record("saludo", p, t)


async def test_busqueda_con_resultados(client: httpx.AsyncClient) -> None:
    section("2. BÚSQUEDA CON RESULTADOS — casa para comprar")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("busco una casa para comprar"))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        props = data.get("propiedades_detalladas", [])
        t += 1; p += check("hay propiedades en respuesta", len(props) > 0,
                            f"got {len(props)}")
        t += 1; p += check("leads=True con propiedades", data.get("leads") is True)
        # Validar estructura de primera propiedad
        if props:
            pp, pt = validate_property_item(props[0], 0)
            p += pp; t += pt
        print(f"  propiedades encontradas: {len(props)}")
        print(f"  tipo[0]: {props[0].get('tipo') if props else 'N/A'!r}")
        print(f"  operacion[0]: {props[0].get('operacion') if props else 'N/A'!r}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}")
    record("busqueda_resultados", p, t)


async def test_sin_resultados(client: httpx.AsyncClient) -> None:
    section("3. BÚSQUEDA SIN RESULTADOS — penthouse en la luna")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("busco un penthouse de lujo con vista al mar en Marte"))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        props = data.get("propiedades_detalladas", [])
        t += 1; p += check("sin propiedades cuando no hay resultados",
                            len(props) == 0, f"got {len(props)}")
        t += 1; p += check("leads=False sin propiedades",
                            data.get("leads") is False)
        print(f"  response[:100]: {data.get('response','')[:100]!r}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}")
    record("sin_resultados", p, t)


async def test_refinamiento(client: httpx.AsyncClient) -> None:
    section("4. REFINAMIENTO — filtrar por dormitorios")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("solo las de 3 dormitorios"))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        print(f"  route: {data.get('metricas', {}).get('route', 'N/A')}")
        print(f"  propiedades: {len(data.get('propiedades_detalladas', []))}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}")
    record("refinamiento", p, t)


async def test_pregunta_kb(client: httpx.AsyncClient) -> None:
    section("5. PREGUNTA KB — comisiones")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("¿cuánto cobran de comisión?"))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        props = data.get("propiedades_detalladas", [])
        t += 1; p += check("KB no devuelve propiedades", len(props) == 0,
                            f"got {len(props)}")
        t += 1; p += check("leads=False en KB", data.get("leads") is False)
        print(f"  route: {data.get('metricas', {}).get('route', 'N/A')}")
        print(f"  response[:120]: {data.get('response','')[:120]!r}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}")
    record("pregunta_kb", p, t)


async def test_captura_lead(client: httpx.AsyncClient) -> None:
    section("6. CAPTURA DE LEAD — datos de contacto")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request(
                              "me llamo Pedro Gonzalez y mi telefono es 351-444-5678, "
                              "quiero que me contacten"
                          ))
    print(f"  HTTP {r.status_code}")
    p = t = 0
    if r.status_code == 200:
        data = r.json()
        rp, rt = validate_base_contract(data)
        p += rp; t += rt
        # En captura de lead el widget solo muestra el texto confirmatorio
        # No debe haber propiedades (ruta contactar_asesor)
        props = data.get("propiedades_detalladas", [])
        t += 1; p += check("sin propiedades en captura de lead",
                            len(props) == 0, f"got {len(props)}")
        print(f"  route: {data.get('metricas', {}).get('route', 'N/A')}")
        print(f"  response[:100]: {data.get('response','')[:100]!r}")
    else:
        t += 1; check("HTTP 200", False, f"got {r.status_code}")
    record("captura_lead", p, t)


async def test_session_consistency(client: httpx.AsyncClient) -> None:
    section("7. CONSISTENCIA DE SESSION ID")
    msgs = [
        "busco departamento en alquiler",
        "que tenga 2 ambientes",
    ]
    p = t = 0
    for i, msg in enumerate(msgs):
        r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                              json=widget_request(msg))
        if r.status_code == 200:
            data = r.json()
            t += 1; ok = check(f"  msg[{i}] sessionId == enviado",
                                data.get("sessionId") == SESSION_ID,
                                f"got {data.get('sessionId')!r}")
            p += ok
        else:
            t += 1; check(f"  msg[{i}] HTTP 200", False, str(r.status_code))
    record("session_consistency", p, t)


async def test_payload_invalido(client: httpx.AsyncClient) -> None:
    section("8. PAYLOAD INVÁLIDO — validación de request")
    p = t = 0

    # Sin mensaje
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json={"sessionId": "test", "timestamp": "", "repo": "bbr"})
    t += 1; p += check("message faltante → 422",
                        r.status_code == 422,
                        f"got {r.status_code}")

    # Mensaje vacío
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json={"message": "", "sessionId": "test"})
    t += 1; p += check("message vacío → 422",
                        r.status_code == 422,
                        f"got {r.status_code}")

    # Slug inexistente → 404 del orchestrator, NO 500
    r = await client.post("/webhook/slug-que-no-existe/chat",
                          json=widget_request("hola"))
    t += 1; p += check("slug inválido → 4xx (no 500)",
                        r.status_code in (404, 422),
                        f"got {r.status_code}")

    # Content-type incorrecto
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          content="no es json",
                          headers={"Content-Type": "text/plain"})
    t += 1; p += check("body no-JSON → 422",
                        r.status_code == 422,
                        f"got {r.status_code}")

    record("payload_invalido", p, t)


async def test_contrato_completo(client: httpx.AsyncClient) -> None:
    """
    Verifica que el response tenga TODOS los campos que el widget puede leer,
    incluyendo los fallbacks (response|respuesta_bot, propiedades_detalladas|propiedades).
    """
    section("9. CONTRATO COMPLETO — todos los campos legacy")
    r = await client.post(f"/webhook/{EMPRESA_SLUG}/chat",
                          json=widget_request("busco casa en venta"))
    p = t = 0
    if r.status_code == 200:
        data = r.json()

        # Campos que el widget lee explícitamente
        campos = {
            "response":                 ("response" in data or "respuesta_bot" in data),
            "propiedades_detalladas":   ("propiedades_detalladas" in data or "propiedades" in data),
            "leads":                    "leads" in data,
            "sessionId":                "sessionId" in data,
            "success":                  "success" in data,
            "timestamp":                "timestamp" in data,
        }
        for campo, present in campos.items():
            t += 1; p += check(f"campo '{campo}' presente", present)

        # Verificar que leads sea EXACTAMENTE bool (el widget usa ===)
        leads = data.get("leads")
        t += 1; p += check("leads es bool (=== compatible)", type(leads) is bool,
                            f"type={type(leads).__name__} value={leads!r}")

        # Verificar que success sea EXACTAMENTE bool
        success = data.get("success")
        t += 1; p += check("success es bool (=== compatible)", type(success) is bool,
                            f"type={type(success).__name__} value={success!r}")

        # propiedades nunca debe ser null (el widget hace .length > 0)
        _props_raw2 = data.get("propiedades_detalladas")
        props = _props_raw2 if _props_raw2 is not None else data.get("propiedades")
        t += 1; p += check("propiedades no es null/None", props is not None)

        print(f"\n  Response completo (campos top-level):")
        for k, v in data.items():
            if k == "propiedades_detalladas":
                print(f"    {k}: [{len(v) if isinstance(v, list) else repr(v)} items]")
            elif k == "response":
                print(f"    {k}: {str(v)[:80]!r}...")
            else:
                print(f"    {k}: {v!r}")
    else:
        t += 1; check("HTTP 200", False, str(r.status_code))
    record("contrato_completo", p, t)


# ─── Runner ───────────────────────────────────────────────────────────────────

async def main() -> None:
    # Parse args simples
    args = sys.argv[1:]
    global BASE_URL, EMPRESA_SLUG
    for i, arg in enumerate(args):
        if arg == "--base-url" and i + 1 < len(args):
            BASE_URL = args[i + 1]
        if arg == "--slug" and i + 1 < len(args):
            EMPRESA_SLUG = args[i + 1]

    print(f"\nInmoBot Premium — E2E Widget Compatibility Tests")
    print(f"  Endpoint: {BASE_URL}/webhook/{EMPRESA_SLUG}/chat")
    print(f"  SessionID: {SESSION_ID}")

    # Verificar que el server esté levantado
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as probe:
            await probe.get("/health")
    except Exception as e:
        print(f"\n[ERROR] No se puede conectar a {BASE_URL}: {e}")
        print("Asegurate de que el server esté levantado con:")
        print("  uvicorn app.main:app --port 8001")
        sys.exit(1)

    # Ejecutar tests secuencialmente (respetan la sesión conversacional)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=40.0) as client:
        await test_saludo(client)
        await test_busqueda_con_resultados(client)
        await test_sin_resultados(client)
        await test_refinamiento(client)
        await test_pregunta_kb(client)
        await test_captura_lead(client)
        await test_session_consistency(client)
        await test_payload_invalido(client)
        await test_contrato_completo(client)

    # Resumen
    print(f"\n{'='*60}")
    print("  RESUMEN FINAL")
    print(f"{'='*60}")
    total_p = total_t = 0
    for r in results:
        status = PASS if r["passed"] == r["total"] else (
            WARN if r["passed"] > 0 else FAIL
        )
        print(f"  {status} {r['scenario']:30s} {r['passed']}/{r['total']}")
        total_p += r["passed"]
        total_t += r["total"]

    pct = round(total_p / total_t * 100) if total_t else 0
    print(f"\n  TOTAL: {total_p}/{total_t} checks pasados ({pct}%)")

    if total_p < total_t:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
