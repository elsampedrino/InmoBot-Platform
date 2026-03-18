"""
FollowupsService — programación de acciones de seguimiento.

Responsabilidades:
- Crear followups cuando el router detecta intención de visita/contacto
- Actualizar estado de followups (pendiente → enviado/cancelado)
- Dejar trazabilidad de las interacciones comerciales posteriores

No debe:
- Reemplazar un CRM completo
- Tomar decisiones autónomas de conversación
- Consultar catálogo
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession


class FollowupsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_followup(
        self,
        id_lead: int,
        id_conversacion: int | None,
        tipo: str,
        fecha_programada: datetime,
        payload: dict | None = None,
    ) -> dict:
        """Crea un followup programado."""
        # TODO Fase 6
        raise NotImplementedError

    async def mark_sent(self, id_followup: int) -> None:
        """Marca un followup como enviado."""
        # TODO Fase 6
        raise NotImplementedError

    async def cancel(self, id_followup: int) -> None:
        """Cancela un followup pendiente."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_pending(self, id_empresa: int) -> list[dict]:
        """Devuelve followups pendientes de ejecutar."""
        # TODO Fase 6
        raise NotImplementedError
