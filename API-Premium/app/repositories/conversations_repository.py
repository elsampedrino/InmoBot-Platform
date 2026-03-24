"""
ConversationsRepository — acceso a conversaciones, mensajes y contextos.

Tablas: conversaciones, mensajes, contextos_conversacion
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.models.db_models import ContextoConversacion, Conversacion, Mensaje


class ConversationsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ─── CONVERSACIONES ───────────────────────────────────────────────────────

    async def get_or_create_conversation(
        self, id_empresa: int, session_id: str, canal: str
    ) -> Conversacion:
        """
        Busca una conversación abierta (fin IS NULL) para la combinación
        id_empresa + session_id. Si no existe, crea una nueva.
        id_lead queda NULL; se vincula cuando hay señal comercial.
        """
        result = await self.db.execute(
            select(Conversacion)
            .where(
                Conversacion.id_empresa == id_empresa,
                Conversacion.session_id == session_id,
                Conversacion.fin.is_(None),
            )
            .order_by(Conversacion.created_at.desc())
            .limit(1)
        )
        conv = result.scalar_one_or_none()

        if conv:
            return conv

        conv = Conversacion(
            id_empresa=id_empresa,
            session_id=session_id,
            canal=canal,
            id_lead=None,
            inicio=datetime.now(timezone.utc),
        )
        self.db.add(conv)
        await self.db.flush()  # obtiene id_conversacion generado
        return conv

    async def get_conversation_by_id(self, id_conversacion: int) -> Conversacion | None:
        result = await self.db.execute(
            select(Conversacion).where(Conversacion.id_conversacion == id_conversacion)
        )
        return result.scalar_one_or_none()

    async def link_lead(self, id_conversacion: int, id_lead: int) -> None:
        """Vincula id_lead a la conversación cuando hay señal comercial."""
        result = await self.db.execute(
            select(Conversacion).where(Conversacion.id_conversacion == id_conversacion)
        )
        conv = result.scalar_one_or_none()
        if conv and conv.id_lead is None:
            conv.id_lead = id_lead
            await self.db.flush()

    # ─── MENSAJES ─────────────────────────────────────────────────────────────

    async def save_message(
        self,
        id_conversacion: int,
        emisor: str,
        mensaje: str,
        raw_payload: dict,
    ) -> Mensaje:
        """Persiste un mensaje en la tabla mensajes."""
        msg = Mensaje(
            id_conversacion=id_conversacion,
            emisor=emisor,
            mensaje=mensaje,
            raw_payload=raw_payload,
        )
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def get_recent_messages(
        self, id_conversacion: int, limit: int
    ) -> list[Mensaje]:
        """
        Devuelve los últimos `limit` mensajes en orden cronológico.
        Se usa para armar el historial reciente del contexto.
        """
        result = await self.db.execute(
            select(Mensaje)
            .where(Mensaje.id_conversacion == id_conversacion)
            .order_by(Mensaje.timestamp.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # orden cronológico ascendente

    # ─── CONTEXTO ─────────────────────────────────────────────────────────────

    async def get_or_create_context(
        self, id_conversacion: int
    ) -> ContextoConversacion:
        """
        Devuelve el contexto existente o crea uno vacío si es la primera vez.
        """
        result = await self.db.execute(
            select(ContextoConversacion).where(
                ContextoConversacion.id_conversacion == id_conversacion
            )
        )
        ctx = result.scalar_one_or_none()

        if ctx:
            return ctx

        ctx = ContextoConversacion(
            id_conversacion=id_conversacion,
            resumen_contexto=None,
            estado_json=None,
        )
        self.db.add(ctx)
        await self.db.flush()
        return ctx

    async def update_context(
        self,
        id_conversacion: int,
        estado_json: dict | None = None,
        resumen_contexto: str | None = None,
    ) -> None:
        """
        Actualiza estado_json y/o resumen_contexto del contexto.
        Solo modifica los campos que recibe (no sobreescribe lo que no se pasa).
        """
        result = await self.db.execute(
            select(ContextoConversacion).where(
                ContextoConversacion.id_conversacion == id_conversacion
            )
        )
        ctx = result.scalar_one_or_none()

        if not ctx:
            ctx = ContextoConversacion(id_conversacion=id_conversacion)
            self.db.add(ctx)

        if estado_json is not None:
            ctx.estado_json = estado_json
            flag_modified(ctx, "estado_json")
        if resumen_contexto is not None:
            ctx.resumen_contexto = resumen_contexto

        await self.db.flush()
