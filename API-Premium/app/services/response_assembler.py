"""
ResponseAssembler — arma el payload de respuesta final para el canal.

Responsabilidades:
- Tomar la salida del flujo (texto IA + items + metadata)
- Formatear según el schema de ChatMessageResponse
- Adjuntar metadata operativa (route, stage, lead_capturado)

No debe:
- Decidir intención
- Volver a buscar datos
- Ejecutar lógica comercial compleja
"""
from app.models.api_models import ChatMessageResponse, ItemBrief
from app.models.domain_models import AssembledResponse


class ResponseAssembler:

    def assemble(
        self,
        session_id: str,
        conversation_id: int | None,
        assembled: AssembledResponse,
    ) -> ChatMessageResponse:
        """Transforma AssembledResponse al schema de la API."""
        # TODO Fase 5
        raise NotImplementedError

    def _to_item_brief(self, item) -> ItemBrief:
        """Convierte un ItemCandidate a ItemBrief para la respuesta."""
        # TODO Fase 5
        raise NotImplementedError
