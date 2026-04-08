"""
NotificationService — notificaciones de nuevos leads por Telegram y Email.

Diseño:
- Fire-and-forget: notify_new_lead() lanza las tareas sin bloquear el flujo principal.
- Cada canal falla de forma independiente y silenciosa (loguea, no propaga).
- La configuración se lee de empresas.notificaciones (JSONB por empresa).
- Invocado exclusivamente desde chat_orchestrator._capture_lead().
"""
import asyncio
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.models.api_models import LeadResponse

logger = get_logger(__name__)


class NotificationService:
    def __init__(self, notificaciones: dict, nombre_empresa: str) -> None:
        """
        notificaciones: valor de empresas.notificaciones (dict).
        nombre_empresa: para el asunto/texto de los mensajes.
        """
        self._cfg = notificaciones or {}
        self._empresa = nombre_empresa

    # ── Punto de entrada ──────────────────────────────────────────────────────

    def notify_new_lead(self, lead: LeadResponse) -> None:
        """
        Lanza las notificaciones habilitadas de forma no bloqueante.
        No hace await — el caller no espera resultado.
        """
        tasks = []

        tg_cfg = self._cfg.get("telegram", {})
        if tg_cfg.get("enabled") and tg_cfg.get("chat_id") and settings.TELEGRAM_BOT_TOKEN:
            tasks.append(self._send_telegram(lead, str(tg_cfg["chat_id"])))

        email_cfg = self._cfg.get("email", {})
        if email_cfg.get("enabled") and email_cfg.get("to") and settings.SMTP_HOST:
            tasks.append(self._send_email(lead, email_cfg["to"]))

        if tasks:
            asyncio.gather(*tasks, return_exceptions=True)

    # ── Telegram ──────────────────────────────────────────────────────────────

    async def _send_telegram(self, lead: LeadResponse, chat_id: str) -> None:
        try:
            text = self._build_telegram_text(lead)
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                })
                if not r.is_success:
                    logger.warning(
                        "telegram_notification_failed",
                        id_lead=lead.id_lead,
                        status=r.status_code,
                        detail=r.text[:200],
                    )
                else:
                    logger.info("telegram_notification_sent", id_lead=lead.id_lead)
        except Exception as exc:
            logger.warning("telegram_notification_error", id_lead=lead.id_lead, error=str(exc))

    def _build_telegram_text(self, lead: LeadResponse) -> str:
        panel_url = f"{settings.PANEL_BASE_URL.rstrip('/')}/leads/{lead.id_lead}"
        propiedades = lead.metadata.get("propiedades_interes", [])

        lines = [
            f"🏠 <b>Nuevo lead — {self._empresa}</b>",
            "",
            f"👤 <b>Nombre:</b> {lead.nombre or '—'}",
            f"📞 <b>Teléfono:</b> {lead.telefono or '—'}",
            f"✉️ <b>Email:</b> {lead.email or '—'}",
            f"📡 <b>Canal:</b> {lead.canal or '—'}",
        ]

        if propiedades:
            lines.append("")
            lines.append("🔍 <b>Propiedades de interés:</b>")
            for p in propiedades[:5]:
                lines.append(f"  · {p}")

        lines += [
            "",
            f"🔗 <a href=\"{panel_url}\">Ver en el panel</a>",
        ]
        return "\n".join(lines)

    # ── Email ─────────────────────────────────────────────────────────────────

    async def _send_email(self, lead: LeadResponse, to: str) -> None:
        try:
            msg = self._build_email(lead, to)
            # SMTP es bloqueante — lo corremos en un executor para no bloquear el event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._smtp_send, msg, to)
            logger.info("email_notification_sent", id_lead=lead.id_lead, to=to)
        except Exception as exc:
            logger.warning("email_notification_error", id_lead=lead.id_lead, error=str(exc))

    def _build_email(self, lead: LeadResponse, to: str) -> MIMEMultipart:
        panel_url = f"{settings.PANEL_BASE_URL.rstrip('/')}/leads/{lead.id_lead}"
        propiedades = lead.metadata.get("propiedades_interes", [])

        subject = f"Nuevo lead — {lead.nombre or 'Sin nombre'} | {self._empresa}"

        props_html = ""
        if propiedades:
            items_html = "".join(f"<li>{p}</li>" for p in propiedades[:5])
            props_html = f"<h3>Propiedades de interés</h3><ul>{items_html}</ul>"

        html = f"""
        <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px;">
          <h2 style="color: #1a56db;">🏠 Nuevo lead — {self._empresa}</h2>
          <table style="border-collapse: collapse; width: 100%;">
            <tr><td style="padding: 8px; font-weight: bold; width: 140px;">Nombre</td>
                <td style="padding: 8px;">{lead.nombre or "—"}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding: 8px; font-weight: bold;">Teléfono</td>
                <td style="padding: 8px;">{lead.telefono or "—"}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Email</td>
                <td style="padding: 8px;">{lead.email or "—"}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding: 8px; font-weight: bold;">Canal</td>
                <td style="padding: 8px;">{lead.canal or "—"}</td></tr>
          </table>
          {props_html}
          <p style="margin-top: 24px;">
            <a href="{panel_url}"
               style="background:#1a56db; color:#fff; padding:10px 20px;
                      border-radius:6px; text-decoration:none; font-weight:bold;">
              Ver en el panel
            </a>
          </p>
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"]      = to
        msg.attach(MIMEText(html, "html"))
        return msg

    def _smtp_send(self, msg: MIMEMultipart, to: str) -> None:
        """Envío SMTP bloqueante — ejecutar en executor."""
        context = ssl.create_default_context()
        if settings.SMTP_SSL:
            # Puerto 465 — SSL directo
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to, msg.as_string())
        else:
            # Puerto 587 — STARTTLS
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to, msg.as_string())