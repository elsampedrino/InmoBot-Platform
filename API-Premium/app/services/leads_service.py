"""
LeadsService — creación y actualización de leads.

Responsabilidades:
- Crear leads cuando hay señal comercial suficiente
- Actualizar datos de contacto (nombre, teléfono, email)
- Registrar señales de interés asociando items
- Vincular lead a conversación

No debe:
- Decidir por sí solo cuándo capturar un lead (eso es el router)
- Gestionar la conversación completa
- Enviar respuestas conversacionales largas
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_models import LeadCreateRequest, LeadListResponse, LeadResponse, LeadUpdateRequest


class LeadsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_lead(self, request: LeadCreateRequest) -> LeadResponse:
        """Crea un nuevo lead."""
        # TODO Fase 6
        raise NotImplementedError

    async def create_from_conversation(
        self,
        id_empresa: int,
        canal: str,
        nombre: str | None = None,
        telefono: str | None = None,
        email: str | None = None,
        metadata: dict | None = None,
    ) -> LeadResponse:
        """
        Crea un lead durante una conversación activa.
        Llamado por el ChatOrchestrator cuando el router detecta señal comercial.
        """
        # TODO Fase 6
        raise NotImplementedError

    async def update_lead(self, id_lead: int, request: LeadUpdateRequest) -> LeadResponse:
        """Actualiza datos de un lead existente."""
        # TODO Fase 6
        raise NotImplementedError

    async def list_leads(
        self,
        id_empresa: int,
        estado: str | None,
        page: int,
        page_size: int,
    ) -> LeadListResponse:
        """Lista paginada de leads de una empresa."""
        # TODO Fase 6
        raise NotImplementedError

    async def get_by_session(self, id_empresa: int, session_id: str) -> LeadResponse | None:
        """Busca un lead existente asociado a un session_id."""
        # TODO Fase 6
        raise NotImplementedError
