"""
KBRepository — acceso a kb_documents y kb_chunks.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import KBChunk, KBDocument


class KBRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_chunks(
        self, id_empresa: int, id_rubro: int, query: str, limit: int = 5
    ) -> list[KBChunk]:
        """Full-text search sobre kb_chunks."""
        raise NotImplementedError

    async def get_document(self, id_documento: uuid.UUID) -> KBDocument | None:
        raise NotImplementedError

    async def list_documents(self, id_empresa: int, id_rubro: int) -> list[KBDocument]:
        raise NotImplementedError
