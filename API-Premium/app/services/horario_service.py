"""
Evalúa si el bot debe responder según bot_mode y horario_config de la empresa.
Desacoplado del canal — reutilizable en WhatsApp y widget web.
"""
from datetime import datetime, time as dtime
import pytz

_TZ = pytz.timezone("America/Argentina/Buenos_Aires")

# Mapeo weekday() de Python (0=lunes) → clave del JSON
_WEEKDAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DEFAULT_HORARIO: dict = {
    "monday":    {"enabled": True,  "from": "09:30", "to": "18:30"},
    "tuesday":   {"enabled": True,  "from": "09:30", "to": "18:30"},
    "wednesday": {"enabled": True,  "from": "09:30", "to": "18:30"},
    "thursday":  {"enabled": True,  "from": "09:30", "to": "18:30"},
    "friday":    {"enabled": True,  "from": "09:30", "to": "18:30"},
    "saturday":  {"enabled": False},
    "sunday":    {"enabled": False},
}


def _parse_time(t: str) -> dtime:
    h, m = t.split(":")
    return dtime(int(h), int(m))


def is_bot_active(empresa) -> tuple[bool, str]:
    """
    Retorna (activo: bool, razon: str).

    razon posibles:
      ""                → bot activo sin restricciones
      "service_disabled"→ servicios.bot == False
      "disabled"        → bot_mode == "disabled"
      "business_hours"  → estamos en horario de oficina (mode=after_hours)
    """
    servicios = empresa.servicios or {}
    if not servicios.get("bot", True):
        return False, "service_disabled"

    mode = empresa.bot_mode or "always_on"

    if mode == "disabled":
        return False, "disabled"

    if mode == "always_on":
        return True, ""

    if mode == "after_hours":
        now = datetime.now(_TZ)
        dia_key = _WEEKDAY_KEYS[now.weekday()]
        horario = empresa.horario_config or DEFAULT_HORARIO
        dia = horario.get(dia_key, {"enabled": False})

        if not dia.get("enabled", False):
            # Oficina cerrada este día → bot activo todo el día
            return True, ""

        hora_abre = _parse_time(dia.get("from", "09:00"))
        hora_cierra = _parse_time(dia.get("to", "18:00"))
        hora_actual = now.time()

        if hora_abre <= hora_actual < hora_cierra:
            return False, "business_hours"

        return True, ""

    # Modo desconocido → activo por defecto
    return True, ""
