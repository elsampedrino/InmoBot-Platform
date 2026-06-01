"""
property_resolver.py — Detecta una propiedad específica en el mensaje entrante.

Flujo Yamila / Houghton:
  Mensaje 1: usuario pega link de pablohoughton.com.ar (o cualquier portal Tokko)
  → extraemos el tokko_id de la URL
  → buscamos en DB por atributos->>'tokko_id'
  → devolvemos los datos del item para inyectarlos en el contexto

Si el mensaje no contiene un link reconocible → retorna None en microsegundos.
Solo activo para rubro inmobiliaria.
"""

import re
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Regex que extrae el Tokko ID de URLs del tipo:
#   https://www.pablohoughton.com.ar/p/7837181-Departamento-en-...
#   https://www.cualquiercliente.com.ar/p/7837181-...  (mismo formato Tokko)
_RE_TOKKO_URL = re.compile(r"/p/(\d+)(?:[/-]|$|\s)")

# También captura IDs de URLs de portales (ZonaProp, Argenprop, etc.)
# que suelen incluir el ID de Tokko en la URL. Patrón más genérico:
_RE_TOKKO_GENERIC = re.compile(r"\b(\d{6,8})\b")


def _extract_tokko_id(text: str) -> str | None:
    """
    Intenta extraer un Tokko ID del texto del mensaje.
    Costo: microsegundos — solo regex, sin DB.
    """
    # Patrón primario: /p/{id}- (sitios propios Tokko)
    m = _RE_TOKKO_URL.search(text)
    if m:
        return m.group(1)
    return None


async def resolve_property(
    message: str,
    id_empresa: int,
    db: AsyncSession,
) -> dict | None:
    """
    Retorna los datos del item si se detecta un Tokko ID en el mensaje.
    Retorna None si no hay match (costo: solo regex → sin latencia).
    """
    tokko_id = _extract_tokko_id(message)
    if not tokko_id:
        return None

    result = await db.execute(
        text("""
            SELECT
                id_item, external_id, tipo, categoria, titulo,
                descripcion_corta, precio, moneda,
                atributos, media
            FROM items
            WHERE id_empresa = :eid
              AND activo = true
              AND atributos->>'tokko_id' = :tid
            LIMIT 1
        """),
        {"eid": id_empresa, "tid": tokko_id},
    )
    row = result.mappings().fetchone()
    if not row:
        logger.info("property_resolver: tokko_id=%s no encontrado para empresa %s", tokko_id, id_empresa)
        return None

    atributos = row["atributos"] or {}
    logger.info(
        "property_resolver: match tokko_id=%s -> %s (%s)",
        tokko_id, row["external_id"], row["titulo"][:40],
    )
    return {
        "id_item":        str(row["id_item"]),
        "external_id":    row["external_id"],
        "tipo":           row["tipo"] or "",
        "categoria":      row["categoria"] or "",
        "titulo":         row["titulo"],
        "descripcion_corta": row["descripcion_corta"],
        "precio":         float(row["precio"]) if row["precio"] is not None else None,
        "moneda":         row["moneda"],
        "atributos":      atributos,
        "calle":          atributos.get("calle", ""),
        "barrio":         atributos.get("barrio", ""),
        "ciudad":         atributos.get("ciudad", ""),
    }
