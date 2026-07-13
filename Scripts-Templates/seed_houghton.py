"""
seed_houghton.py — Crea la empresa Houghton Inmobiliaria y carga su catalogo.

Uso:
  cd c:/Desarrollo/InmoBot/ChatBOT-Inmobiliaria-VCode
  python Scripts-Templates/seed_houghton.py
"""
import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "API-Premium"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql+asyncpg://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI"
    "@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"
)

ID_RUBRO_INMOBILIARIA = 1
ID_PLAN_BASICO        = 1

# Campos extra para propiedades demo — responden preguntas frecuentes de Yamila
DEMO_ENRICHMENT: dict[str, dict] = {
    "PROP-001": {
        "disponibilidad": {"estado": "libre", "disponible_desde": "inmediata", "se_puede_visitar": True},
        "gastos": {"expensas": 95000, "expensas_moneda": "ARS", "abl": 18000, "incluye_impuestos": False},
        "extras": {"orientacion": "norte", "apto_profesional": True, "piso": 3, "tiene_ascensor": True, "antiguedad_edificio": 2},
    },
    "PROP-003": {
        "disponibilidad": {"estado": "ocupado", "disponible_desde": "01/08/2026", "se_puede_visitar": True},
        "gastos": {"expensas": 78000, "expensas_moneda": "ARS", "abl": 14000, "incluye_impuestos": False},
        "extras": {"orientacion": "contrafrente", "apto_profesional": False, "piso": 1, "tiene_ascensor": True, "antiguedad_edificio": 15},
    },
    "PROP-005": {
        "disponibilidad": {"estado": "libre", "disponible_desde": "inmediata", "se_puede_visitar": True},
        "gastos": {"expensas": 110000, "expensas_moneda": "ARS", "abl": 22000, "incluye_impuestos": False},
        "extras": {"orientacion": "norte", "apto_profesional": True, "piso": 7, "tiene_ascensor": True, "antiguedad_edificio": 5},
    },
    "PROP-010": {
        "disponibilidad": {"estado": "ocupado", "situacion": "habitada", "disponible_desde": "a convenir", "se_puede_visitar": True},
        "gastos": {"expensas": None, "expensas_moneda": "ARS", "abl": 18000, "incluye_impuestos": False, "nota": "Sin expensas. ABL e impuestos municipales a cargo del comprador."},
        "extras": {"pileta": True, "quincho": True, "cochera_fija": True, "cocheras": 4, "apto_mascotas": True, "jardin": True},
    },
    "PROP-015": {
        "disponibilidad": {"estado": "ocupado", "disponible_desde": "a convenir", "se_puede_visitar": False},
        "gastos": {"expensas": 38000, "expensas_moneda": "ARS", "abl": 7500, "incluye_impuestos": False},
        "extras": {"cuatro_vientos": False, "rubros_aptos": ["consultorio", "estudio juridico", "oficina"], "se_puede_habilitar": True},
    },
}


def build_atributos(prop: dict, extra: dict) -> dict:
    """
    El search engine espera los campos al primer nivel del JSONB:
      atributos->>'barrio', atributos->>'dormitorios', etc.
    Aplanamos direccion{} y caracteristicas{} al nivel raiz.
    """
    dir_   = prop.get("direccion", {}) or {}
    carac  = prop.get("caracteristicas", {}) or {}

    atributos = {
        # Direccion aplanada
        "calle":   dir_.get("calle"),
        "barrio":  dir_.get("barrio"),
        "ciudad":  dir_.get("ciudad"),
        "lat":     dir_.get("lat"),
        "lng":     dir_.get("lng"),
        # Caracteristicas aplanadas
        "antiguedad":          carac.get("antiguedad"),
        "estado_construccion": carac.get("estado_construccion"),
        "ambientes":           carac.get("ambientes"),
        "dormitorios":         carac.get("dormitorios"),
        "banios":              carac.get("banios"),
        "superficie_total":    carac.get("superficie_total"),
        "superficie_cubierta": carac.get("superficie_cubierta"),
        # Detalles (array — ya estaba OK)
        "detalles": prop.get("detalles", []),
    }
    # Campos demo enriquecidos (disponibilidad, gastos, extras)
    atributos.update(extra)
    return atributos


async def run():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:

        # 1. Empresa
        res = await session.execute(
            text("SELECT id_empresa FROM empresas WHERE slug = 'houghton'")
        )
        row = res.fetchone()
        if row:
            id_empresa = row[0]
            print(f"[OK] Empresa ya existe  id_empresa={id_empresa}")
        else:
            res2 = await session.execute(
                text("""
                    INSERT INTO empresas
                        (nombre, slug, id_plan, activa, timezone, servicios, notificaciones)
                    VALUES (
                        'Houghton Inmobiliaria', 'houghton', :plan, true,
                        'America/Argentina/Buenos_Aires',
                        CAST(:servicios AS jsonb),
                        CAST(:notificaciones AS jsonb)
                    )
                    RETURNING id_empresa
                """),
                {
                    "plan": ID_PLAN_BASICO,
                    "servicios": '{"bot": true}',
                    "notificaciones": '{"telegram":{"enabled":false,"chat_id":""},"email":{"enabled":false,"to":""}}',
                },
            )
            id_empresa = res2.fetchone()[0]
            print(f"[OK] Empresa creada  id_empresa={id_empresa}")

        # 2. EmpresaRubro
        er = await session.execute(
            text("SELECT 1 FROM empresa_rubros WHERE id_empresa=:e AND id_rubro=:r"),
            {"e": id_empresa, "r": ID_RUBRO_INMOBILIARIA},
        )
        if not er.fetchone():
            await session.execute(
                text("INSERT INTO empresa_rubros (id_empresa, id_rubro, activo, es_default) VALUES (:e, :r, true, true)"),
                {"e": id_empresa, "r": ID_RUBRO_INMOBILIARIA},
            )
            print("[OK] EmpresaRubro creada  inmobiliaria_demo es_default=True")
        else:
            print("[OK] EmpresaRubro ya existe")

        # 3. Items
        json_path = Path(__file__).parent.parent / "Inmob Houghton" / "propiedades_houghton.json"
        data = json.loads(json_path.read_text(encoding="utf-8-sig"))
        propiedades = data["propiedades"]

        inserted = updated = 0

        for prop in propiedades:
            ext_id    = prop["id"]
            extra     = DEMO_ENRICHMENT.get(ext_id, {})
            atributos = json.dumps(build_atributos(prop, extra), ensure_ascii=False)
            media     = json.dumps({"fotos": prop.get("fotos", {}).get("urls") or []}, ensure_ascii=False)
            precio    = prop.get("precio", {}).get("valor")
            moneda    = prop.get("precio", {}).get("moneda", "USD")

            ex_item = await session.execute(
                text("SELECT id_item FROM items WHERE id_empresa=:e AND external_id=:eid"),
                {"e": id_empresa, "eid": ext_id},
            )
            if ex_item.fetchone():
                await session.execute(
                    text("""
                        UPDATE items SET
                            tipo=:tipo, categoria=:cat, titulo=:titulo,
                            descripcion=:desc, descripcion_corta=:desc_corta,
                            precio=:precio, moneda=:moneda,
                            activo=:activo, destacado=:destacado,
                            atributos=CAST(:atributos AS jsonb),
                            media=CAST(:media AS jsonb)
                        WHERE id_empresa=:e AND external_id=:eid
                    """),
                    {"tipo": prop["tipo"], "cat": prop.get("operacion"), "titulo": prop["titulo"],
                     "desc": prop.get("descripcion"), "desc_corta": prop.get("descripcion_corta"),
                     "precio": precio, "moneda": moneda,
                     "activo": prop.get("activo", True), "destacado": prop.get("destacado", False),
                     "atributos": atributos, "media": media,
                     "e": id_empresa, "eid": ext_id},
                )
                updated += 1
            else:
                await session.execute(
                    text("""
                        INSERT INTO items
                            (id_item, id_empresa, id_rubro, external_id,
                             tipo, categoria, titulo, descripcion, descripcion_corta,
                             precio, moneda, activo, destacado,
                             atributos, media)
                        VALUES (
                            :id, :e, :r, :eid,
                            :tipo, :cat, :titulo, :desc, :desc_corta,
                            :precio, :moneda, :activo, :destacado,
                            CAST(:atributos AS jsonb), CAST(:media AS jsonb)
                        )
                    """),
                    {"id": str(uuid.uuid4()), "e": id_empresa, "r": ID_RUBRO_INMOBILIARIA, "eid": ext_id,
                     "tipo": prop["tipo"], "cat": prop.get("operacion"), "titulo": prop["titulo"],
                     "desc": prop.get("descripcion"), "desc_corta": prop.get("descripcion_corta"),
                     "precio": precio, "moneda": moneda,
                     "activo": prop.get("activo", True), "destacado": prop.get("destacado", False),
                     "atributos": atributos, "media": media},
                )
                inserted += 1

        await session.commit()

        print(f"[OK] Items insertados: {inserted}  actualizados: {updated}")
        print(f"[OK] Props demo enriquecidas: {[k for k in DEMO_ENRICHMENT if k in {p['id'] for p in propiedades}]}")
        print(f"[DONE] Houghton lista  slug='houghton'  id={id_empresa}  total={len(propiedades)} props")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
