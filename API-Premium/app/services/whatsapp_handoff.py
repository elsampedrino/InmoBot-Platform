"""
whatsapp_handoff.py — Generador de payload de handoff hacia WhatsApp humano.

Diseñado para ser reutilizable en el futuro:
- Hoy: deep link wa.me con mensaje pre-cargado → humano
- Futuro: Meta Cloud API, WhatsApp Business, automatizaciones
"""
import urllib.parse

from app.models.api_models import ItemBrief


def _build_message(items: list[ItemBrief], lead_nombre: str | None = None) -> str:
    lines: list[str] = []

    if lead_nombre:
        lines.append(f"Hola, soy {lead_nombre}.")
    else:
        lines.append("Hola,")

    lines.append("consulté desde la web sobre:")
    lines.append("")

    if items:
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
) -> dict:
    """
    Genera el payload de handoff a WhatsApp.

    Retorna dict con:
      enabled, url, phone, agent_name, message

    Desacoplado del widget y del canal de origen — reutilizable para
    Meta API, WhatsApp conversacional y automatizaciones.
    """
    message = _build_message(items, lead_nombre)
    url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"

    return {
        "enabled": True,
        "url": url,
        "phone": phone,
        "agent_name": agent_name or "Asesor",
        "message": message,
    }
