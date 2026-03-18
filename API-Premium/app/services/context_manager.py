"""
ContextManager — gestiona el estado conversacional multi-turno.

Responsabilidades:
- Recuperar o crear una Conversacion para el session_id + empresa
- Leer el ContextoConversacion (resumen + estado_json)
- Deserializar el ConversationState estructurado
- Proveer el TurnContext completo para el pipeline
- Persistir mensajes (user + bot)
- Actualizar estado y resumen al cierre del turno
- Vincular lead cuando hay señal comercial

No debe:
- Decidir rutas ni ejecutar lógica de negocio
- Consultar el catálogo directamente
"""
from app.core.config import settings
from app.core.logging import get_logger
from app.models.domain_models import ConversationState, TenantConfig, TurnContext
from app.repositories.conversations_repository import ConversationsRepository

logger = get_logger(__name__)


class ContextManager:
    def __init__(self, db) -> None:
        self.db = db
        self._repo = ConversationsRepository(db)

    # ─── Carga del turno ──────────────────────────────────────────────────────

    async def load_turn_context(
        self,
        id_empresa: int,
        id_rubro: int,
        canal: str,
        session_id: str,
        mensaje: str,
        tenant_config: TenantConfig,
    ) -> TurnContext:
        """
        Punto de entrada principal del ContextManager.
        Carga (o crea) la conversación y devuelve el TurnContext completo.

        - La conversación se crea al primer mensaje (sin lead aún).
        - El estado estructurado se deserializa desde estado_json.
        - Los mensajes recientes se cargan para el historial de la IA.
        """
        # 1. Conversación activa o nueva
        conv = await self._repo.get_or_create_conversation(
            id_empresa, session_id, canal
        )

        # 2. Contexto (resumen + estado_json)
        ctx = await self._repo.get_or_create_context(conv.id_conversacion)

        # 3. Deserializar estado estructurado
        state = (
            ConversationState.from_dict(ctx.estado_json)
            if ctx.estado_json
            else ConversationState()
        )

        # 4. Mensajes recientes (ventana configurable)
        recent = await self._repo.get_recent_messages(
            conv.id_conversacion, settings.CONTEXT_WINDOW_MESSAGES
        )
        mensajes_recientes = [
            {
                "role": "user" if m.emisor == "user" else "assistant",
                "content": m.mensaje,
            }
            for m in recent
        ]

        logger.debug(
            "turn_context_loaded",
            id_conversacion=conv.id_conversacion,
            session_id=session_id,
            stage=state.conversation_stage.value,
            mensajes_previos=len(mensajes_recientes),
        )

        return TurnContext(
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            canal=canal,
            session_id=session_id,
            mensaje=mensaje,
            id_conversacion=conv.id_conversacion,
            conversation_state=state,
            resumen_contexto=ctx.resumen_contexto,
            mensajes_recientes=mensajes_recientes,
            tenant_config=tenant_config,
        )

    # ─── Persistencia de mensajes ─────────────────────────────────────────────

    async def save_user_message(
        self,
        id_conversacion: int,
        mensaje: str,
        raw_payload: dict,
    ) -> None:
        """Persiste el mensaje entrante del usuario."""
        await self._repo.save_message(
            id_conversacion=id_conversacion,
            emisor="user",
            mensaje=mensaje,
            raw_payload=raw_payload,
        )

    async def save_bot_message(
        self,
        id_conversacion: int,
        mensaje: str,
    ) -> None:
        """Persiste la respuesta generada por el bot."""
        await self._repo.save_message(
            id_conversacion=id_conversacion,
            emisor="bot",
            mensaje=mensaje,
            raw_payload={},
        )

    # ─── Actualización del contexto ───────────────────────────────────────────

    async def update_context(
        self,
        id_conversacion: int,
        state: ConversationState,
        resumen: str | None = None,
    ) -> None:
        """
        Persiste el estado estructurado y opcionalmente el resumen.
        Solo actualiza resumen si se pasa explícitamente (no lo sobreescribe con None).
        """
        await self._repo.update_context(
            id_conversacion=id_conversacion,
            estado_json=state.to_dict(),
            resumen_contexto=resumen,
        )

        logger.debug(
            "context_updated",
            id_conversacion=id_conversacion,
            stage=state.conversation_stage.value,
            route=state.route_actual,
        )

    # ─── Vinculación de lead ──────────────────────────────────────────────────

    async def link_lead(self, id_conversacion: int, id_lead: int) -> None:
        """
        Vincula un lead a la conversación.
        Llamado por el Orchestrator cuando hay señal comercial suficiente.
        """
        await self._repo.link_lead(id_conversacion, id_lead)
        logger.info(
            "lead_linked_to_conversation",
            id_conversacion=id_conversacion,
            id_lead=id_lead,
        )

    # ─── Historial reciente ───────────────────────────────────────────────────

    async def get_recent_messages(
        self, id_conversacion: int, limit: int
    ) -> list[dict]:
        """
        Devuelve los últimos `limit` mensajes formateados para la API de Anthropic.
        Formato: [{"role": "user"|"assistant", "content": str}]
        """
        recent = await self._repo.get_recent_messages(id_conversacion, limit)
        return [
            {
                "role": "user" if m.emisor == "user" else "assistant",
                "content": m.mensaje,
            }
            for m in recent
        ]
