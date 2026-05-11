"""
whatsapp_handoff.py — Generador de payload de handoff hacia WhatsApp humano.

Diseñado para ser reutilizable en el futuro:
- Hoy: deep link wa.me con mensaje pre-cargado → humano
- Futuro: Meta Cloud API, WhatsApp Business, automatizaciones
"""
import urllib.parse

from app.models.api_models import ItemBrief


def _build_message(
    items: list[ItemBrief],
    lead_nombre: str | None = None,
    propiedades_interes: list[dict] | None = None,
) -> str:
    lines: list[str] = []

    if lead_nombre:
        lines.append(f"Hola, soy {lead_nombre}.")
    else:
        lines.append("Hola,")

    lines.append("consulté desde la web sobre:")
    lines.append("")

    if items:
        # Datos frescos del turno actual (rara vez — solo si la búsqueda ocurrió en este turno)
        prop = items[0]
        lines.append(f"{prop.id_item} - {prop.titulo}")
        atrib = prop.atributos or {}
        partes: list[str] = []
        if atrib.get("calle"):
            partes.append(str(atrib["calle"]))
        if atrib.get("barrio"):
            partes.append(str(atrib["barrio"]))
        if atrib.get("ciudad"):
            partes.append(str(atrib["ciudad"]))
        if partes:
            lines.append(", ".join(partes))
    elif propiedades_interes:
        # Datos enriquecidos del estado conversacional (caso habitual en el handoff de WA)
        prop = propiedades_interes[0]
        titulo = prop.get("titulo", "")
        tipo = prop.get("tipo", "")
        categoria = prop.get("categoria", "")
        precio = prop.get("precio")
        moneda = prop.get("moneda", "USD")
        barrio = prop.get("barrio") or prop.get("ciudad", "")

        lines.append(titulo)

        tipo_cat_parts = []
        if tipo:
            tipo_cat_parts.append(tipo.capitalize())
        if categoria:
            tipo_cat_parts.append(f"en {categoria}")
        if tipo_cat_parts:
            lines.append(" ".join(tipo_cat_parts))

        if barrio:
            lines.append(f"Ubicación: {barrio}")

        if precio and precio > 0:
            precio_fmt = f"{int(precio):,}".replace(",", ".")
            lines.append(f"Precio: {moneda} {precio_fmt}")
    else:
        lines.append("propiedades disponibles")

    lines.append("")
    lines.append("Me gustaría recibir más información o coordinar una visita.")

    return "\n".join(lines)


def build_whatsapp_handoff(
    phone: str,
    agent_name: str,
    items: list[ItemBrief],
    lead_nombre: str | None = None,
    propiedades_interes: list[dict] | None = None,
) -> dict:
    """
    Genera el payload de handoff a WhatsApp.

    Retorna dict con:
      enabled, url, phone, agent_name, message

    Desacoplado del widget y del canal de origen — reutilizable para
    Meta API, WhatsApp conversacional y automatizaciones.
    """
    message = _build_message(items, lead_nombre, propiedades_interes)
    url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"

    return {
        "enabled": True,
        "url": url,
        "phone": phone,
        "agent_name": agent_name or "Asesor",
        "message": message,
    }
