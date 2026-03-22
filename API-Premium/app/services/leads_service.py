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
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.api_models import LeadCreateRequest, LeadListResponse, LeadResponse, LeadUpdateRequest
from app.models.db_models import Lead
from app.repositories.leads_repository import LeadsRepository

logger = get_logger(__name__)


def _lead_to_response(lead: Lead) -> LeadResponse:
    return LeadResponse(
        id_lead=lead.id_lead,
        id_empresa=lead.id_empresa,
        nombre=lead.nombre,
        telefono=lead.telefono,
        email=lead.email,
        canal=lead.canal,
        estado=lead.estado,
        metadata=lead.metadata_ or {},
    )


class LeadsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = LeadsRepository(db)

    async def create_lead(self, request: LeadCreateRequest) -> LeadResponse:
        """Crea un nuevo lead (uso administrativo / externo)."""
        lead = await self._repo.create(
            id_empresa=request.id_empresa,
            canal=request.canal,
            nombre=request.nombre,
            telefono=request.telefono,
            email=request.email,
            metadata=request.metadata or {},
        )
        return _lead_to_response(lead)

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

        Al menos uno de nombre, telefono o email debe estar presente para que
        el lead tenga valor. Si ninguno está presente se crea igual con los
        datos de metadata (session_id, route, etc.) para trazabilidad.
        """
        lead = await self._repo.create(
            id_empresa=id_empresa,
            canal=canal,
            nombre=nombre,
            telefono=telefono,
            email=email,
            metadata=metadata or {},
        )
        logger.info(
            "lead_created_from_conversation",
            id_lead=lead.id_lead,
            tiene_nombre=nombre is not None,
            tiene_telefono=telefono is not None,
            tiene_email=email is not None,
        )
        return _lead_to_response(lead)

    async def update_lead(self, id_lead: int, request: LeadUpdateRequest) -> LeadResponse:
        """Actualiza datos de un lead existente."""
        # Construir dict con los campos a actualizar (solo los no-None)
        data: dict = {}
        if request.nombre is not None:
            data["nombre"] = request.nombre
        if request.telefono is not None:
            data["telefono"] = request.telefono
        if request.email is not None:
            data["email"] = request.email
        if request.estado is not None:
            data["estado"] = request.estado
        if request.metadata is not None:
            data["metadata_"] = request.metadata  # atributo Python, no columna

        if not data:
            # Nada que actualizar — devolver el estado actual
            lead = await self._repo.get_by_id(id_lead)
            if lead is None:
                raise HTTPException(status_code=404, detail="Lead no encontrado")
            return _lead_to_response(lead)

        try:
            lead = await self._repo.update(id_lead, data)
        except ValueError:
            raise HTTPException(status_code=404, detail="Lead no encontrado")

        return _lead_to_response(lead)

    async def list_leads(
        self,
        id_empresa: int,
        estado: str | None,
        page: int,
        page_size: int,
    ) -> LeadListResponse:
        """Lista paginada de leads de una empresa."""
        offset = (page - 1) * page_size
        leads, total = await self._repo.list_by_empresa(
            id_empresa=id_empresa,
            estado=estado,
            offset=offset,
            limit=page_size,
        )
        return LeadListResponse(
            leads=[_lead_to_response(l) for l in leads],
            total=total,
        )

    async def get_by_session(self, id_empresa: int, session_id: str) -> LeadResponse | None:
        """
        Busca un lead vinculado a una sesión específica.
        La búsqueda se hace por el session_id guardado en metadata_
        durante create_from_conversation().
        """
        # Usamos una query raw porque SQLAlchemy no tiene JSONB contains nativo
        # sin extensiones adicionales. Por ahora retornamos None (sin deduplicar).
        # El orquestador crea un lead por señal de contacto detectada.
        # TODO: implementar deduplicación por session_id si es necesario.
        logger.debug("get_by_session_not_implemented", session_id=session_id)
        return None
