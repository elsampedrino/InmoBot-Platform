"""
importaciones_repository.py — Lógica de diff y upsert masivo de catálogo.
No llama a db.commit() — el router es responsable de hacer commit/rollback.
"""
import json
import uuid
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ImportacionLog, Item


# ─── Conversión JSON landing → campos DB ─────────────────────────────────────

def _json_to_db_fields(prop: dict) -> dict:
    """Convierte un item del formato propiedades_bbr.json a campos DB normalizados."""
    addr = prop.get("direccion") or {}
    chars = prop.get("caracteristicas") or {}
    precio_obj = prop.get("precio") or {}
    fotos_obj = prop.get("fotos") or {}

    precio_val = precio_obj.get("valor")
    precio_float = float(precio_val) if precio_val is not None else None

    atributos: dict[str, Any] = {
        "calle": addr.get("calle") or None,
        "barrio": addr.get("barrio") or None,
        "ciudad": addr.get("ciudad") or None,
        "lat": addr.get("lat"),
        "lng": addr.get("lng"),
        "expensas": precio_obj.get("expensas"),
        "antiguedad": chars.get("antiguedad") or None,
        "estado_construccion": chars.get("estado_construccion") or None,
        "ambientes": chars.get("ambientes"),
        "dormitorios": chars.get("dormitorios"),
        "banios": chars.get("banios"),
        "superficie_total": chars.get("superficie_total") or None,
        "superficie_cubierta": chars.get("superficie_cubierta") or None,
        "detalles": prop.get("detalles") or [],
    }

    return {
        "external_id": str(prop["id"]).strip(),
        "tipo": (prop.get("tipo") or "").lower().strip(),
        "categoria": (prop.get("operacion") or "").lower().strip() or None,
        "titulo": (prop.get("titulo") or "").strip(),
        "descripcion": prop.get("descripcion") or None,
        "descripcion_corta": prop.get("descripcion_corta") or None,
        "precio": precio_float,
        "moneda": precio_obj.get("moneda") or None,
        "activo": bool(prop.get("activo", True)),
        "destacado": bool(prop.get("destacado", False)),
        "atributos": atributos,
        "media": {"fotos": fotos_obj.get("urls") or []},
    }


# ─── Diff ─────────────────────────────────────────────────────────────────────

_SCALAR_FIELDS = ["tipo", "categoria", "titulo", "descripcion", "descripcion_corta",
                   "moneda", "activo", "destacado"]
_COMPARE_FIELDS = _SCALAR_FIELDS + ["precio"]


def _fields_differ(incoming: dict, db_row: dict) -> list[str]:
    """Devuelve lista de nombres de campo que difieren entre incoming y db_row."""
    diffs: list[str] = []

    for f in _SCALAR_FIELDS:
        v_inc = incoming.get(f)
        v_db = db_row.get(f)
        # Normalizar None y ""
        v_inc = None if v_inc == "" else v_inc
        v_db = None if v_db == "" else v_db
        if v_inc != v_db:
            diffs.append(f)

    # precio: comparar como float
    p_inc = incoming.get("precio")
    p_db = db_row.get("precio")
    if p_db is not None:
        p_db = float(p_db)
    if p_inc != p_db:
        diffs.append("precio")

    # atributos y media: comparación estructural
    if incoming.get("atributos") != db_row.get("atributos"):
        diffs.append("atributos")
    if incoming.get("media") != db_row.get("media"):
        diffs.append("media")

    return diffs


async def get_items_for_diff(db: AsyncSession, id_empresa: int) -> dict[str, dict]:
    """Devuelve todos los items de la empresa como dict {external_id: row_dict}."""
    sql = text("""
        SELECT
            id_item::text, external_id, tipo, categoria, titulo,
            descripcion, descripcion_corta,
            precio::float AS precio, moneda,
            activo, destacado, atributos, media
        FROM items
        WHERE id_empresa = :id_empresa
    """)
    result = await db.execute(sql, {"id_empresa": id_empresa})
    rows = result.mappings().all()
    return {r["external_id"]: dict(r) for r in rows}


def compute_diff(
    db_items: dict[str, dict],
    incoming_props: list[dict],
) -> dict:
    """
    Calcula el diff entre el catálogo entrante y el estado actual en DB.
    Returns dict con: nuevos, modificados, sin_cambios, a_desactivar.
    """
    nuevos = []
    modificados = []
    sin_cambios = 0
    incoming_ids: set[str] = set()

    for prop in incoming_props:
        fields = _json_to_db_fields(prop)
        ext_id = fields["external_id"]
        incoming_ids.add(ext_id)

        if ext_id not in db_items:
            nuevos.append({
                "external_id": ext_id,
                "titulo": fields["titulo"],
                "tipo": fields["tipo"],
                "categoria": fields["categoria"],
                "_fields": fields,
            })
        else:
            diffs = _fields_differ(fields, db_items[ext_id])
            if diffs:
                modificados.append({
                    "external_id": ext_id,
                    "titulo": fields["titulo"],
                    "tipo": fields["tipo"],
                    "categoria": fields["categoria"],
                    "cambios": diffs,
                    "_fields": fields,
                })
            else:
                sin_cambios += 1

    # Items en DB activos que no están en el JSON
    a_desactivar = [
        {
            "external_id": ext_id,
            "titulo": row["titulo"],
            "tipo": row["tipo"],
            "categoria": row.get("categoria"),
        }
        for ext_id, row in db_items.items()
        if ext_id not in incoming_ids and row["activo"]
    ]

    return {
        "nuevos": nuevos,
        "modificados": modificados,
        "sin_cambios": sin_cambios,
        "a_desactivar": a_desactivar,
    }


# ─── Upsert ───────────────────────────────────────────────────────────────────

async def apply_diff(
    db: AsyncSession,
    id_empresa: int,
    id_rubro: int,
    nuevos: list[dict],
    modificados: list[dict],
    a_desactivar: list[dict],
) -> tuple[int, int, int]:
    """
    Aplica el diff calculado por compute_diff a la DB.
    - nuevos: insertar items nuevos
    - modificados: actualizar campos cambiados
    - a_desactivar: poner activo=False

    Nota: no hace commit — el router es responsable.
    """
    insertados = 0
    actualizados = 0
    desactivados = 0

    # Insertar nuevos
    for item_data in nuevos:
        fields = item_data["_fields"]
        item = Item(
            id_item=uuid.uuid4(),
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            external_id=fields["external_id"],
            tipo=fields["tipo"],
            categoria=fields["categoria"],
            titulo=fields["titulo"],
            descripcion=fields.get("descripcion"),
            descripcion_corta=fields.get("descripcion_corta"),
            precio=fields.get("precio"),
            moneda=fields.get("moneda"),
            activo=fields["activo"],
            destacado=fields["destacado"],
            atributos=fields["atributos"],
            media=fields["media"],
        )
        db.add(item)
        insertados += 1

    await db.flush()

    # Actualizar modificados
    for item_data in modificados:
        fields = item_data["_fields"]
        ext_id = fields["external_id"]
        await db.execute(
            text("""
                UPDATE items SET
                    tipo = :tipo,
                    categoria = :categoria,
                    titulo = :titulo,
                    descripcion = :descripcion,
                    descripcion_corta = :descripcion_corta,
                    precio = :precio,
                    moneda = :moneda,
                    activo = :activo,
                    destacado = :destacado,
                    atributos = :atributos::jsonb,
                    media = :media::jsonb,
                    updated_at = now()
                WHERE id_empresa = :id_empresa AND external_id = :external_id
            """),
            {
                "tipo": fields["tipo"],
                "categoria": fields["categoria"],
                "titulo": fields["titulo"],
                "descripcion": fields.get("descripcion"),
                "descripcion_corta": fields.get("descripcion_corta"),
                "precio": fields.get("precio"),
                "moneda": fields.get("moneda"),
                "activo": fields["activo"],
                "destacado": fields["destacado"],
                "atributos": json.dumps(fields["atributos"]),
                "media": json.dumps(fields["media"]),
                "id_empresa": id_empresa,
                "external_id": ext_id,
            },
        )
        actualizados += 1

    # Desactivar
    if a_desactivar:
        ids_to_deactivate = [item["external_id"] for item in a_desactivar]
        await db.execute(
            text("""
                UPDATE items SET activo = false, updated_at = now()
                WHERE id_empresa = :id_empresa AND external_id = ANY(:ids)
            """),
            {"id_empresa": id_empresa, "ids": ids_to_deactivate},
        )
        desactivados = len(ids_to_deactivate)

    return insertados, actualizados, desactivados


# ─── Logs ─────────────────────────────────────────────────────────────────────

async def create_log(db: AsyncSession, data: dict) -> ImportacionLog:
    """Crea un registro de log. No hace commit."""
    log = ImportacionLog(
        id_empresa=data["id_empresa"],
        accion=data["accion"],
        resultado=data["resultado"],
        detalle=data.get("detalle", {}),
        id_usuario=data.get("id_usuario"),
        nombre_usuario=data.get("nombre_usuario"),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def list_logs(
    db: AsyncSession,
    id_empresa: int,
    limit: int = 20,
) -> tuple[list[ImportacionLog], int]:
    from sqlalchemy.orm import selectinload

    q = (
        select(ImportacionLog)
        .where(ImportacionLog.id_empresa == id_empresa)
        .options(selectinload(ImportacionLog.empresa))
        .order_by(ImportacionLog.created_at.desc())
    )
    total_q = select(func.count()).select_from(
        select(ImportacionLog).where(ImportacionLog.id_empresa == id_empresa).subquery()
    )
    total = (await db.execute(total_q)).scalar_one()
    rows = (await db.execute(q.limit(limit))).scalars().all()
    return list(rows), total