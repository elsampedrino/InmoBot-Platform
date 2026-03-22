"""
Seed items from propiedades_bbr.json → tabla items de PostgreSQL.

Uso:
    cd API-Premium
    python scripts/seed_items_bbr.py                    # usa empresa slug='cristian-inmob'
    python scripts/seed_items_bbr.py --slug bbr-otro    # otro slug
    python scripts/seed_items_bbr.py --dry-run          # solo muestra, no inserta

Mapeo:
    JSON .operacion        → items.categoria
    JSON .precio.valor     → items.precio
    JSON .precio.moneda    → items.moneda
    JSON .direccion + .caracteristicas + .detalles → items.atributos JSONB
    JSON .fotos.urls       → items.media JSONB {"fotos": [...]}
    UUID determinístico    → uuid5(NAMESPACE, "bbr-{prop_id}")
"""
import asyncio
import json
import sys
import uuid
from pathlib import Path

# Agregar el parent al path para importar la app
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg

from app.core.config import settings

# ─── Namespace para UUIDs determinísticos ────────────────────────────────────
_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # uuid.NAMESPACE_URL

# ─── Path al JSON ────────────────────────────────────────────────────────────
_JSON_PATH = Path(__file__).parent.parent.parent / "BBR Grupo Inmobiliario" / "propiedades_bbr.json"


def prop_to_item(prop: dict, id_empresa: int, id_rubro: int) -> dict:
    """Convierte una propiedad del JSON al formato de la tabla items."""
    prop_id = prop["id"]
    item_uuid = uuid.uuid5(_NS, f"bbr-{prop_id}")

    direccion = prop.get("direccion", {})
    precio_obj = prop.get("precio", {})
    caract = prop.get("caracteristicas", {})
    detalles = prop.get("detalles", [])

    atributos = {
        "prop_id": prop_id,                          # id original del JSON (para trazabilidad)
        "calle": direccion.get("calle") or "",
        "barrio": direccion.get("barrio") or "",
        "ciudad": direccion.get("ciudad") or "",
        "lat": direccion.get("lat"),
        "lng": direccion.get("lng"),
        "ambientes": caract.get("ambientes"),
        "dormitorios": caract.get("dormitorios"),
        "banios": caract.get("banios"),
        "antiguedad": caract.get("antigüedad"),
        "estado_construccion": caract.get("estado_construccion"),
        "superficie_total": caract.get("superficie_total"),
        "superficie_cubierta": caract.get("superficie_cubierta"),
        "expensas": precio_obj.get("expensas"),
        "detalles": detalles,
    }

    fotos = prop.get("fotos", {}).get("urls", [])
    media = {"fotos": fotos}

    precio_val = precio_obj.get("valor")
    precio_final = float(precio_val) if precio_val and precio_val > 0 else None

    return {
        "id_item": str(item_uuid),
        "id_empresa": id_empresa,
        "id_rubro": id_rubro,
        "external_id": prop_id,                   # ID original del JSON ("PROP-001")
        "tipo": prop.get("tipo", "propiedad"),
        "categoria": prop.get("operacion"),       # "venta" | "alquiler" | "alquiler_temporario"
        "titulo": prop.get("titulo", ""),
        "descripcion": prop.get("descripcion"),
        "descripcion_corta": prop.get("descripcion_corta"),
        "precio": precio_final,
        "moneda": precio_obj.get("moneda", "USD"),
        "activo": prop.get("activo", True),
        "destacado": prop.get("destacado", False),
        "atributos": json.dumps(atributos, ensure_ascii=False),
        "media": json.dumps(media, ensure_ascii=False),
    }


async def seed(slug: str, dry_run: bool) -> None:
    # Extraer DSN asyncpg (reemplazar +asyncpg por nada)
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    if not _JSON_PATH.exists():
        print(f"ERROR: No se encontró el JSON en {_JSON_PATH}")
        sys.exit(1)

    with open(_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    propiedades = data.get("propiedades", [])
    print(f"JSON cargado: {len(propiedades)} propiedades")

    conn = await asyncpg.connect(dsn)
    try:
        # Resolver empresa + rubro
        row = await conn.fetchrow(
            "SELECT id_empresa FROM empresas WHERE slug = $1 AND activa = TRUE", slug
        )
        if not row:
            print(f"ERROR: Empresa con slug='{slug}' no encontrada o inactiva.")
            sys.exit(1)
        id_empresa = row["id_empresa"]

        rubro_row = await conn.fetchrow(
            """SELECT er.id_rubro FROM empresa_rubros er
               WHERE er.id_empresa = $1 AND er.activo = TRUE
               ORDER BY er.es_default DESC LIMIT 1""",
            id_empresa
        )
        if not rubro_row:
            print(f"ERROR: No hay rubro activo para empresa id={id_empresa}")
            sys.exit(1)
        id_rubro = rubro_row["id_rubro"]

        print(f"Empresa: id={id_empresa}, slug='{slug}'  |  Rubro: id={id_rubro}")

        items = []
        for prop in propiedades:
            if not prop.get("activo", True):
                continue
            items.append(prop_to_item(prop, id_empresa, id_rubro))

        print(f"Items a insertar: {len(items)}")

        if dry_run:
            for it in items[:3]:
                print(f"  DRY-RUN: {it['tipo']} / {it['categoria']} | {it['titulo'][:60]}")
            print("  ... (dry-run, no se insertó nada)")
            return

        # Upsert: INSERT ... ON CONFLICT (id_item) DO UPDATE
        result = await conn.executemany(
            """INSERT INTO items
               (id_item, id_empresa, id_rubro, external_id, tipo, categoria, titulo,
                descripcion, descripcion_corta, precio, moneda,
                activo, destacado, atributos, media)
               VALUES
               ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14::jsonb, $15::jsonb)
               ON CONFLICT (id_empresa, external_id) DO UPDATE SET
                 tipo             = EXCLUDED.tipo,
                 categoria        = EXCLUDED.categoria,
                 titulo           = EXCLUDED.titulo,
                 descripcion      = EXCLUDED.descripcion,
                 descripcion_corta= EXCLUDED.descripcion_corta,
                 precio           = EXCLUDED.precio,
                 moneda           = EXCLUDED.moneda,
                 activo           = EXCLUDED.activo,
                 destacado        = EXCLUDED.destacado,
                 atributos        = EXCLUDED.atributos,
                 media            = EXCLUDED.media,
                 updated_at       = NOW()""",
            [
                (
                    it["id_item"], it["id_empresa"], it["id_rubro"],
                    it["external_id"], it["tipo"], it["categoria"], it["titulo"],
                    it["descripcion"], it["descripcion_corta"], it["precio"], it["moneda"],
                    it["activo"], it["destacado"], it["atributos"], it["media"],
                )
                for it in items
            ],
        )
        print(f"OK Upsert completado: {len(items)} items procesados")

        # Resumen
        resumen = await conn.fetch(
            "SELECT tipo, categoria, COUNT(*) AS n FROM items WHERE id_empresa=$1 GROUP BY tipo, categoria ORDER BY n DESC",
            id_empresa
        )
        print("\nResumen en DB:")
        for r in resumen:
            print(f"  {r['n']:>3}x  {r['tipo']} / {r['categoria']}")

    finally:
        await conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="cristian-inmob", help="Slug de la empresa")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra, no inserta")
    args = parser.parse_args()

    asyncio.run(seed(args.slug, args.dry_run))
