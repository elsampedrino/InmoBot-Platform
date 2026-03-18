"""
KBService — consulta la knowledge base de la empresa.

Responsabilidades:
- Buscar en kb_documents y kb_chunks según empresa y rubro
- Recuperar contenido institucional (horarios, comisiones, documentación, etc.)
- Preparar el contexto de KB para que la IA redacte la respuesta

No debe:
- Reemplazar la búsqueda de catálogo
- Capturar leads directamente
- Definir el estilo global de respuesta
"""
from sqlalchemy.ext.asyncio import AsyncSession


class KBService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(self, id_empresa: int, id_rubro: int, query: str) -> list[dict]:
        """
        Busca fragmentos relevantes en kb_chunks usando full-text search (tsvector).
        Devuelve una lista de chunks ordenados por relevancia.
        """
        # TODO Fase 6
        raise NotImplementedError

    async def get_document(self, id_empresa: int, id_documento: str) -> dict | None:
        """Devuelve un documento completo de la KB."""
        # TODO Fase 6
        raise NotImplementedError
