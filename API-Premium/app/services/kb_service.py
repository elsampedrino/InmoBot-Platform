"""
KBService — consulta la knowledge base de la empresa.

Responsabilidades:
- Coordinar búsquedas en kb_documents / kb_chunks vía KBRepository
- Devolver chunks relevantes como lista de dicts para el PromptService
- Registrar si la búsqueda usó FTS o fallback ILIKE

Principio:
  La KB es la fuente de verdad para preguntas institucionales.
  KBService provee el contenido; Sonnet solo redacta la respuesta.
  Si no hay contenido suficiente, el sistema lo indica explícitamente.

No debe:
- Redactar respuestas
- Reemplazar la búsqueda de catálogo
- Capturar leads
"""
from app.core.logging import get_logger
from app.repositories.kb_repository import KBRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

# Máximo de chunks a pasar al PromptService.
# Más chunks = mejor cobertura, pero más tokens en Sonnet.
_MAX_CHUNKS_FOR_PROMPT = 4


class KBService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = KBRepository(db)

    async def search(
        self,
        id_empresa: int,
        id_rubro: int,
        query: str,
        limit: int = _MAX_CHUNKS_FOR_PROMPT,
    ) -> list[dict]:
        """
        Busca chunks relevantes en la KB para la query dada.

        Devuelve lista de dicts con:
          - chunk_texto: str      — contenido del chunk
          - doc_titulo: str       — título del documento fuente
          - id_chunk: str         — UUID del chunk
          - id_documento: str     — UUID del documento
          - search_method: str    — "fts" | "ilike"

        Si no hay resultados, devuelve lista vacía.
        El caller debe tratar lista vacía como "sin contenido KB".
        """
        if not query or not query.strip():
            logger.debug("kb_search_empty_query")
            return []

        chunks = await self._repo.search_chunks(
            id_empresa=id_empresa,
            id_rubro=id_rubro,
            query=query.strip(),
            limit=limit,
        )

        logger.info(
            "kb_search_completed",
            id_empresa=id_empresa,
            query_len=len(query),
            chunks_found=len(chunks),
            method=chunks[0]["search_method"] if chunks else "none",
        )

        return chunks

    async def list_documents(
        self, id_empresa: int, id_rubro: int
    ) -> list[dict]:
        """Lista documentos activos — útil para admin / debug."""
        return await self._repo.list_documents(id_empresa, id_rubro)
