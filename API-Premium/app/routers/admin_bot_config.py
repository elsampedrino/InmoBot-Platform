"""
GET  /admin/bot-config  → devuelve bot_mode + horario_config de la empresa del usuario logueado
PUT  /admin/bot-config  → actualiza bot_mode (solo always_on/after_hours) y horario_config

Solo accesible por usuarios autenticados. El cliente no puede establecer mode=disabled.
El superadmin puede establecer cualquier mode via EmpresaFormPage.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.admin_auth import get_current_admin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin
from app.services.horario_service import DEFAULT_HORARIO

router = APIRouter()

# Modos que el cliente puede seleccionar (disabled es solo superadmin)
_CLIENT_ALLOWED_MODES = {"always_on", "after_hours"}


class BotConfigResponse(BaseModel):
    bot_mode: str
    horario_config: dict[str, Any]


class BotConfigRequest(BaseModel):
    bot_mode: str
    horario_config: dict[str, Any] | None = None

    @field_validator("bot_mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in _CLIENT_ALLOWED_MODES:
            raise ValueError(f"Modo inválido. Opciones: {', '.join(_CLIENT_ALLOWED_MODES)}")
        return v


@router.get("", response_model=BotConfigResponse)
async def get_bot_config(
    current_user: UsuarioAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> BotConfigResponse:
    empresa = current_user.empresa
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return BotConfigResponse(
        bot_mode=empresa.bot_mode or "always_on",
        horario_config=empresa.horario_config or DEFAULT_HORARIO,
    )


@router.put("", response_model=BotConfigResponse)
async def update_bot_config(
    body: BotConfigRequest,
    current_user: UsuarioAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> BotConfigResponse:
    empresa = current_user.empresa
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    empresa.bot_mode = body.bot_mode
    if body.horario_config is not None:
        empresa.horario_config = body.horario_config

    await db.commit()
    await db.refresh(empresa)

    return BotConfigResponse(
        bot_mode=empresa.bot_mode,
        horario_config=empresa.horario_config or DEFAULT_HORARIO,
    )
