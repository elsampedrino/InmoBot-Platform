"""
Endpoints de autenticación del panel admin.

POST /admin/auth/login           — recibe email + password, devuelve JWT + contexto
GET  /admin/auth/me              — devuelve usuario y empresa del token actual
POST /admin/auth/change-password — cambia contraseña (requiere auth)
POST /admin/auth/forgot-password — solicita reset por email (público)
POST /admin/auth/reset-password  — confirma reset con token (público)
"""
import asyncio
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt as _bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.admin_auth import create_access_token, get_current_admin
from app.core.config import settings
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin
import app.repositories.usuarios_repository as repo

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class EmpresaInfo(BaseModel):
    id_empresa: int
    nombre: str
    slug: str | None
    servicios: dict


class UsuarioInfo(BaseModel):
    id_usuario: int
    nombre: str | None
    email: str
    es_superadmin: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioInfo
    empresa: EmpresaInfo


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _check_panel_cliente(user: UsuarioAdmin) -> None:
    """Raise 403 PANEL_DISABLED for non-superadmin when panel_cliente service is off."""
    if user.es_superadmin:
        return
    servicios = user.empresa.servicios or {}
    if not servicios.get("panel_cliente", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PANEL_DISABLED", "message": "El panel de cliente no está habilitado para esta empresa."},
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioAdmin)
        .where(UsuarioAdmin.email == body.email, UsuarioAdmin.activo == True)  # noqa: E712
        .options(selectinload(UsuarioAdmin.empresa))
    )
    user = result.scalar_one_or_none()

    if not user or not _bcrypt.checkpw(body.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    _check_panel_cliente(user)

    empresa = user.empresa
    token = create_access_token(user.id_usuario, empresa.slug or "")

    return LoginResponse(
        access_token=token,
        usuario=UsuarioInfo(
            id_usuario=user.id_usuario,
            nombre=user.nombre,
            email=user.email,
            es_superadmin=user.es_superadmin,
        ),
        empresa=EmpresaInfo(
            id_empresa=empresa.id_empresa,
            nombre=empresa.nombre,
            slug=empresa.slug,
            servicios=empresa.servicios or {"bot": True},
        ),
    )


@router.get("/me", response_model=LoginResponse)
async def me(current_user: UsuarioAdmin = Depends(get_current_admin)):
    _check_panel_cliente(current_user)

    empresa = current_user.empresa
    token = create_access_token(current_user.id_usuario, empresa.slug or "")

    return LoginResponse(
        access_token=token,
        usuario=UsuarioInfo(
            id_usuario=current_user.id_usuario,
            nombre=current_user.nombre,
            email=current_user.email,
            es_superadmin=current_user.es_superadmin,
        ),
        empresa=EmpresaInfo(
            id_empresa=empresa.id_empresa,
            nombre=empresa.nombre,
            slug=empresa.slug,
            servicios=empresa.servicios or {"bot": True},
        ),
    )


# ─── Schemas adicionales ──────────────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password_nueva: str


# ─── Helper email ─────────────────────────────────────────────────────────────

PANEL_URL = "https://panel.automatizacionia.com.ar"

def _send_reset_email(to: str, token: str) -> None:
    reset_link = f"{PANEL_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto">
      <h2 style="color:#1e3a5f">Restablecer contraseña</h2>
      <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en InmoBot.</p>
      <p>Hacé clic en el botón para crear una nueva contraseña. El link es válido por <strong>30 minutos</strong>.</p>
      <p style="text-align:center;margin:32px 0">
        <a href="{reset_link}"
           style="background:#2563eb;color:#fff;padding:12px 28px;border-radius:8px;
                  text-decoration:none;font-weight:bold;font-size:15px">
          Restablecer contraseña
        </a>
      </p>
      <p style="color:#6b7280;font-size:13px">
        Si no solicitaste esto, podés ignorar este correo. Tu contraseña no va a cambiar.
      </p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
      <p style="color:#9ca3af;font-size:12px">InmoBot — Panel Administrativo</p>
    </div>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Restablecer contraseña — InmoBot"
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    if settings.SMTP_SSL:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=ctx) as srv:
            srv.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            srv.sendmail(msg["From"], to, msg.as_string())
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as srv:
            srv.ehlo()
            srv.starttls(context=ctx)
            srv.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            srv.sendmail(msg["From"], to, msg.as_string())


# ─── Endpoints adicionales ────────────────────────────────────────────────────

@router.post("/change-password", status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    current_user: UsuarioAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not _bcrypt.checkpw(body.password_actual.encode(), current_user.password_hash.encode()):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")
    if len(body.password_nueva) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres.")
    await repo.reset_password(db, current_user, body.password_nueva)
    await db.commit()


@router.post("/forgot-password", status_code=204)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await repo.get_usuario_by_email(db, body.email)
    if not user or not user.activo:
        return  # Respuesta idéntica aunque el email no exista (evitar enumeración)

    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    await repo.set_reset_token(db, user, token, expiry)
    await db.commit()

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _send_reset_email, user.email, token)
    except Exception:
        pass


@router.post("/reset-password", status_code=204)
async def reset_password_endpoint(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await repo.get_by_reset_token(db, body.token)
    if not user or not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="El link de restablecimiento es inválido o ya fue utilizado.")

    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(status_code=400, detail="El link expiró. Solicitá uno nuevo.")

    if len(body.password_nueva) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

    await repo.reset_password(db, user, body.password_nueva)
    await repo.clear_reset_token(db, user)
    await db.commit()