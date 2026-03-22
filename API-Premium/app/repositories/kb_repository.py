"""
KBRepository — acceso a kb_documents y kb_chunks.

Estrategia de búsqueda (simple, sin embeddings):
  1. Full-text search PostgreSQL con plainto_tsquery('spanish', :query)
  2. Si FTS devuelve 0 resultados → fallback ILIKE por keyword

La separación en dos queries hace que el fallback sea explícito y logueable.
"""
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)

# Número máximo de chunks devueltos por búsqueda
_CHUNK_LIMIT = 5


class KBRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_chunks(
        self,
        id_empresa: int,
        id_rubro: int,
        query: str,
        limit: int = _CHUNK_LIMIT,
    ) -> list[dict]:
        """
        Búsqueda en dos pasos:
          1. FTS con plainto_tsquery('spanish') → ranking por relevancia
          2. Fallback ILIKE si FTS no devuelve resultados

        Devuelve lista de dicts con: id_chunk, chunk_texto, orden,
        doc_titulo, id_documento, search_method.
        """
        # ── Paso 1: Full-text search ────────────────────────────────────────
        # Incluye el título del documento + unaccent para manejar queries sin tilde.
        # unaccent('documentacion') = unaccent('documentación') → mismo stem.
        fts_sql = text("""
            SELECT
                kc.id_chunk::text,
                kc.chunk_texto,
                kc.orden,
                kd.titulo        AS doc_titulo,
                kd.id_documento::text,
                ts_rank(
                    to_tsvector('spanish', unaccent(kd.titulo || ' ' || kc.chunk_texto)),
                    plainto_tsquery('spanish', unaccent(:query))
                )                AS rank
            FROM kb_chunks kc
            JOIN kb_documents kd ON kd.id_documento = kc.id_documento
            WHERE kd.id_empresa = :id_empresa
              AND kd.id_rubro   = :id_rubro
              AND kd.activo     = TRUE
              AND to_tsvector('spanish', unaccent(kd.titulo || ' ' || kc.chunk_texto))
                  @@ plainto_tsquery('spanish', unaccent(:query))
            ORDER BY rank DESC, kc.orden ASC
            LIMIT :limit
        """)

        try:
            result = await self.db.execute(
                fts_sql,
                {"id_empresa": id_empresa, "id_rubro": id_rubro,
                 "query": query, "limit": limit},
            )
            rows = [dict(r) for r in result.mappings()]
        except Exception as exc:
            # plainto_tsquery puede fallar con queries muy cortos o caracteres raros
            logger.warning("kb_fts_error", error=str(exc), query=query)
            rows = []

        if rows:
            for r in rows:
                r["search_method"] = "fts"
            logger.debug("kb_fts_results", count=len(rows), query=query)
            return rows

        # ── Paso 2: Fallback ILIKE ──────────────────────────────────────────
        # Toma el término más largo del query como keyword principal
        keyword = max(query.split(), key=len) if query.strip() else query

        ilike_sql = text("""
            SELECT
                kc.id_chunk::text,
                kc.chunk_texto,
                kc.orden,
                kd.titulo AS doc_titulo,
                kd.id_documento::text
            FROM kb_chunks kc
            JOIN kb_documents kd ON kd.id_documento = kc.id_documento
            WHERE kd.id_empresa = :id_empresa
              AND kd.id_rubro   = :id_rubro
              AND kd.activo     = TRUE
              AND (unaccent(kc.chunk_texto) ILIKE unaccent(:pattern)
                OR unaccent(kd.titulo) ILIKE unaccent(:pattern))
            ORDER BY kc.orden ASC
            LIMIT :limit
        """)

        result = await self.db.execute(
            ilike_sql,
            {"id_empresa": id_empresa, "id_rubro": id_rubro,
             "pattern": f"%{keyword}%", "limit": limit},
        )
        rows = [dict(r) for r in result.mappings()]

        for r in rows:
            r["search_method"] = "ilike"
        logger.debug("kb_ilike_results", count=len(rows), keyword=keyword)
        return rows

    async def get_document(
        self, id_empresa: int, id_documento: str
    ) -> dict | None:
        """Devuelve un documento completo por id (UUID string)."""
        sql = text("""
            SELECT
                id_documento::text,
                id_empresa,
                titulo,
                contenido_texto,
                activo,
                version,
                created_at
            FROM kb_documents
            WHERE id_empresa  = :id_empresa
              AND id_documento = cast(:id_documento as uuid)
              AND activo       = TRUE
        """)
        result = await self.db.execute(
            sql, {"id_empresa": id_empresa, "id_documento": id_documento}
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def list_documents(
        self, id_empresa: int, id_rubro: int
    ) -> list[dict]:
        """Lista todos los documentos activos de la empresa/rubro."""
        sql = text("""
            SELECT
                id_documento::text,
                titulo,
                activo,
                version,
                created_at
            FROM kb_documents
            WHERE id_empresa = :id_empresa
              AND id_rubro   = :id_rubro
              AND activo     = TRUE
            ORDER BY created_at DESC
        """)
        result = await self.db.execute(
            sql, {"id_empresa": id_empresa, "id_rubro": id_rubro}
        )
        return [dict(r) for r in result.mappings()]
