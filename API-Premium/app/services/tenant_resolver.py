"""
TenantResolver — resuelve empresa, rubro y configuración completa para el turno.

Responsabilidades:
- Buscar empresa por slug y validar que esté activa
- Cargar rubro, su schema de búsqueda y los prompts activos
- Cargar overrides de prompt de la empresa (brand_voice, prompt_extra)
- Cargar límites del plan
- Devolver TenantConfig listo para ser usado en el turno

No debe:
- Ejecutar búsquedas de catálogo
- Generar respuestas
- Capturar leads
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db_models import (
    Empresa,
    EmpresaPromptOverride,
    EmpresaRubro,
    Plan,
    RubroPrompt,
    RubroSchema,
)
from app.models.domain_models import TenantConfig

logger = get_logger(__name__)

# Valores por defecto cuando la empresa no tiene prompts configurados
_DEFAULT_SYSTEM_PROMPT = (
    "Sos un asistente virtual inmobiliario amigable y profesional. "
    "Tu objetivo es ayudar al usuario a encontrar la propiedad ideal "
    "respondiendo sus consultas de forma clara, concisa y empática."
)


class TenantResolver:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def resolve(
        self, empresa_slug: str, id_rubro: int | None = None
    ) -> TenantConfig:
        """
        Resuelve la configuración completa del tenant a partir del slug.

        Args:
            empresa_slug: Slug único de la empresa (ej: "bbr-inmobiliaria")
            id_rubro: Rubro a usar. Si None, se usa el rubro por defecto de la empresa.

        Raises:
            HTTPException 404: Empresa no encontrada.
            HTTPException 403: Empresa inactiva.
        """
        empresa = await self._get_empresa(empresa_slug)
        effective_rubro_id = id_rubro or await self._get_default_rubro_id(empresa.id_empresa)

        rubro_prompt, rubro_schema, override, plan = await self._load_config(
            empresa.id_empresa, effective_rubro_id, empresa.id_plan
        )

        logger.info(
            "tenant_resolved",
            slug=empresa_slug,
            id_empresa=empresa.id_empresa,
            id_rubro=effective_rubro_id,
            has_prompt=rubro_prompt is not None,
            has_override=override is not None,
        )

        return TenantConfig(
            id_empresa=empresa.id_empresa,
            id_rubro=effective_rubro_id,
            nombre_empresa=empresa.nombre,
            slug=empresa.slug,
            system_prompt=(
                rubro_prompt.system_prompt if rubro_prompt else _DEFAULT_SYSTEM_PROMPT
            ),
            style_prompt=rubro_prompt.style_prompt if rubro_prompt else None,
            brand_voice=override.brand_voice if override else None,
            prompt_extra=override.prompt_extra if override else None,
            max_items_per_response=settings.MAX_ITEMS_PER_RESPONSE,
            ia_habilitada=plan.ia_habilitada if plan else True,
            followup_habilitado=empresa.permite_followup,
            search_mode=(
                rubro_schema.search_mode if rubro_schema else "items_structured"
            ),
            facet_keys=list(rubro_schema.facet_keys) if rubro_schema else [],
            validation_rules=dict(rubro_schema.validation_rules) if rubro_schema else {},
        )

    # ─── Helpers privados ─────────────────────────────────────────────────────

    async def _get_default_rubro_id(self, id_empresa: int) -> int:
        """
        Devuelve el id_rubro por defecto de la empresa desde empresa_rubros.
        Si no hay ninguno marcado como default, toma el primero activo.
        Si no tiene rubros asignados, devuelve 1 como fallback.
        """
        result = await self.db.execute(
            select(EmpresaRubro)
            .where(
                EmpresaRubro.id_empresa == id_empresa,
                EmpresaRubro.activo == True,  # noqa: E712
            )
            .order_by(EmpresaRubro.es_default.desc())
            .limit(1)
        )
        er = result.scalar_one_or_none()
        return er.id_rubro if er else 1

    async def _get_empresa(self, slug: str) -> Empresa:
        result = await self.db.execute(
            select(Empresa).where(Empresa.slug == slug)
        )
        empresa = result.scalar_one_or_none()

        if empresa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con slug '{slug}' no encontrada.",
            )
        if not empresa.activa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Empresa '{slug}' está inactiva.",
            )
        return empresa

    async def _load_config(
        self,
        id_empresa: int,
        id_rubro: int,
        id_plan: int | None,
    ) -> tuple[RubroPrompt | None, RubroSchema | None, EmpresaPromptOverride | None, Plan | None]:
        """Carga en paralelo los 4 recursos de configuración del tenant."""

        # Prompt activo del rubro (versión más alta)
        prompt_q = await self.db.execute(
            select(RubroPrompt)
            .where(
                RubroPrompt.id_rubro == id_rubro,
                RubroPrompt.activo == True,  # noqa: E712
            )
            .order_by(RubroPrompt.version.desc())
            .limit(1)
        )
        rubro_prompt = prompt_q.scalar_one_or_none()

        # Schema del rubro (búsqueda, facetas, validaciones)
        schema_q = await self.db.execute(
            select(RubroSchema).where(RubroSchema.id_rubro == id_rubro)
        )
        rubro_schema = schema_q.scalar_one_or_none()

        # Override de prompt activo de la empresa
        override_q = await self.db.execute(
            select(EmpresaPromptOverride).where(
                EmpresaPromptOverride.id_empresa == id_empresa,
                EmpresaPromptOverride.activo == True,  # noqa: E712
            )
        )
        override = override_q.scalar_one_or_none()

        # Plan de la empresa
        plan = None
        if id_plan:
            plan_q = await self.db.execute(
                select(Plan).where(Plan.id_plan == id_plan)
            )
            plan = plan_q.scalar_one_or_none()

        return rubro_prompt, rubro_schema, override, plan
