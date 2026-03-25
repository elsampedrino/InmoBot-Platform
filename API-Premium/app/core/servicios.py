"""
Helpers para control de servicios por empresa.

Uso en endpoints sensibles:

    from app.core.servicios import require_servicio

    @router.post("/items/export-github")
    async def export_github(
        _: None = Depends(require_servicio("landing")),
        ...
    ):
        ...
"""
from fastapi import Depends, HTTPException, status

from app.models.domain_models import TenantConfig


def require_servicio(nombre: str):
    """
    Dependency factory que valida que la empresa tenga activo el servicio indicado.

    Lanza 403 si el servicio no está en empresa.servicios o su valor es False.
    """
    def _check(tenant_config: TenantConfig) -> None:
        if not tenant_config.servicios.get(nombre, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La empresa no tiene contratado el servicio '{nombre}'.",
            )
    return Depends(_check)