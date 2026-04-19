"""
admin_instagram.py — Publicación de propiedades en Instagram (V1 manual).

Endpoints:
  GET  /admin/instagram/config/{id_empresa}   → estado de config (superadmin)
  PUT  /admin/instagram/config/{id_empresa}   → guardar/actualizar config (superadmin)
  GET  /admin/instagram/preview/{id_item}     → imagen + caption + última publicación
  POST /admin/instagram/publish               → publica en Instagram Graph API y persiste

Seguridad:
  - access_token nunca se devuelve en responses
  - publicaciones filtradas por id_empresa del usuario logueado
  - propiedad inactiva bloquea la publicación (no solo advertencia)
"""
import json
from datetime import date, datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import get_current_admin, require_superadmin
from app.core.database import get_db
from app.models.db_models import UsuarioAdmin

router = APIRouter()

_IG_API_BASE = "https://graph.facebook.com/v19.0"
_CAPTION_MAX_LEN = 2200


# ─── Modelos ──────────────────────────────────────────────────────────────────

class InstagramConfigStatus(BaseModel):
    id_empresa: int
    ig_user_id: str
    token_configured: bool
    token_expires_at: str | None


class InstagramConfigUpdate(BaseModel):
    ig_user_id: str
    access_token: str | None = None      # None = mantener el existente
    token_expires_at: str | None = None  # ISO string o None


class InstagramPreviewResponse(BaseModel):
    id_item: str
    external_id: str
    titulo: str
    image_url: str | None
    caption: str
    item_activo: bool
    instagram_configurado: bool
    ultima_publicacion: dict | None      # status, published_at, provider_post_id


class InstagramPublishRequest(BaseModel):
    id_item: str
    caption: str


class InstagramPublishResult(BaseModel):
    status: str
    provider_post_id: str | None
    published_at: str | None
    error_message: str | None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _generate_caption(titulo: str, tipo: str | None, precio: float | None, moneda: str | None, atributos: dict) -> str:
    lines = [f"🏠 {titulo}", ""]

    if precio and float(precio) > 0:
        precio_fmt = f"{int(precio):,}".replace(",", ".")
        lines.append(f"💰 {moneda or 'USD'} {precio_fmt}")

    dormitorios = atributos.get("dormitorios") or atributos.get("ambientes")
    banos = atributos.get("banos") or atributos.get("baños") or atributos.get("cantidad_banos")
    if dormitorios or banos:
        hab = []
        if dormitorios: hab.append(f"🛏 {dormitorios} dorm.")
        if banos:       hab.append(f"🚿 {banos} baños")
        lines.append(" · ".join(hab))

    superficie = atributos.get("superficie_cubierta") or atributos.get("superficie_total")
    if superficie:
        lines.append(f"📐 {superficie} m²")

    partes = [p for p in [atributos.get("barrio"), atributos.get("ciudad")] if p]
    if partes:
        lines.append(f"📍 {', '.join(partes)}")

    if atributos.get("pileta") or atributos.get("piscina"):
        lines.append("🏊 Con pileta")
    elif atributos.get("cochera"):
        lines.append("🚗 Con cochera")
    elif atributos.get("jardin") or atributos.get("jardín"):
        lines.append("🌿 Con jardín")

    lines += ["", "¡Consultanos sin compromiso!", ""]

    hashtags = ["#inmobiliaria", "#propiedades", "#bienesraices"]
    if ciudad := atributos.get("ciudad"):
        slug = ciudad.lower()
        for src, dst in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),(" ","")]:
            slug = slug.replace(src, dst)
        hashtags.insert(1, f"#{slug}")
    tipo_tags = {"casa": "#casas", "departamento": "#departamentos", "local": "#locales",
                 "terreno": "#terrenos", "lote": "#lotes", "campo": "#campos"}
    if tipo and (tag := tipo_tags.get(tipo.lower())):
        hashtags.append(tag)

    lines.append(" ".join(hashtags))
    return "\n".join(lines)


def _extract_image_url(media: dict | None) -> str | None:
    if not media:
        return None
    fotos = media.get("fotos", [])
    if isinstance(fotos, list) and fotos:
        return str(fotos[0])
    if isinstance(fotos, dict):
        urls = fotos.get("urls", [])
        return str(urls[0]) if urls else None
    return None


async def _get_ig_config(db: AsyncSession, id_empresa: int) -> dict | None:
    row = await db.execute(
        text("SELECT ig_user_id, access_token, token_expires_at FROM empresa_instagram_config WHERE id_empresa = :emp"),
        {"emp": id_empresa},
    )
    r = row.mappings().first()
    return dict(r) if r else None


# ─── Config endpoints (superadmin) ───────────────────────────────────────────

@router.get("/config/{id_empresa}", response_model=InstagramConfigStatus)
async def get_instagram_config(
    id_empresa: int,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(require_superadmin),
):
    cfg = await _get_ig_config(db, id_empresa)
    if not cfg:
        raise HTTPException(status_code=404, detail="Instagram no configurado para esta empresa")
    return InstagramConfigStatus(
        id_empresa        = id_empresa,
        ig_user_id        = cfg["ig_user_id"],
        token_configured  = bool(cfg["access_token"]),
        token_expires_at  = cfg["token_expires_at"].isoformat() if cfg["token_expires_at"] else None,
    )


@router.put("/config/{id_empresa}", response_model=InstagramConfigStatus)
async def upsert_instagram_config(
    id_empresa: int,
    body: InstagramConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: UsuarioAdmin = Depends(require_superadmin),
):
    existing = await _get_ig_config(db, id_empresa)

    # Parsear fecha si viene como string ISO (ej: "2026-06-19")
    expires_parsed = None
    if body.token_expires_at:
        try:
            expires_parsed = datetime.fromisoformat(body.token_expires_at).date() \
                if "T" in body.token_expires_at \
                else date.fromisoformat(body.token_expires_at)
        except ValueError:
            expires_parsed = None

    if existing:
        # UPDATE — solo actualiza access_token si se provee uno nuevo
        token_to_save = body.access_token.strip() if body.access_token and body.access_token.strip() else existing["access_token"]
        await db.execute(text("""
            UPDATE empresa_instagram_config
               SET ig_user_id        = :uid,
                   access_token      = :token,
                   token_expires_at  = :expires,
                   updated_at        = NOW()
             WHERE id_empresa = :emp
        """), {
            "uid":     body.ig_user_id.strip(),
            "token":   token_to_save,
            "expires": expires_parsed,
            "emp":     id_empresa,
        })
    else:
        # INSERT — token obligatorio en alta
        if not body.access_token or not body.access_token.strip():
            raise HTTPException(status_code=422, detail="El access_token es obligatorio al configurar Instagram por primera vez")
        await db.execute(text("""
            INSERT INTO empresa_instagram_config (id_empresa, ig_user_id, access_token, token_expires_at)
            VALUES (:emp, :uid, :token, :expires)
        """), {
            "emp":     id_empresa,
            "uid":     body.ig_user_id.strip(),
            "token":   body.access_token.strip(),
            "expires": expires_parsed,
        })

    await db.commit()
    cfg = await _get_ig_config(db, id_empresa)
    return InstagramConfigStatus(
        id_empresa       = id_empresa,
        ig_user_id       = cfg["ig_user_id"],
        token_configured = True,
        token_expires_at = cfg["token_expires_at"].isoformat() if cfg["token_expires_at"] else None,
    )


# ─── Preview ─────────────────────────────────────────────────────────────────

@router.get("/preview/{id_item}", response_model=InstagramPreviewResponse)
async def get_instagram_preview(
    id_item: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    emp = current_user.id_empresa

    item_row = await db.execute(text("""
        SELECT id_item::text, external_id, titulo, tipo, precio, moneda, activo, atributos, media
        FROM items
        WHERE id_item = :item_id AND id_empresa = :emp
    """), {"item_id": id_item, "emp": emp})
    item = item_row.mappings().first()
    if not item:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    atributos = item["atributos"] or {}
    if isinstance(atributos, str):
        atributos = json.loads(atributos)

    media = item["media"] or {}
    if isinstance(media, str):
        media = json.loads(media)

    image_url = _extract_image_url(media)
    caption   = _generate_caption(
        titulo    = item["titulo"],
        tipo      = item["tipo"],
        precio    = item["precio"],
        moneda    = item["moneda"],
        atributos = atributos,
    )

    # Última publicación para esta propiedad
    last_row = await db.execute(text("""
        SELECT status, provider_post_id, published_at, created_at
        FROM instagram_posts
        WHERE id_item = :item_id AND id_empresa = :emp
        ORDER BY created_at DESC
        LIMIT 1
    """), {"item_id": id_item, "emp": emp})
    last = last_row.mappings().first()
    ultima = {
        "status":           last["status"],
        "provider_post_id": last["provider_post_id"],
        "published_at":     last["published_at"].isoformat() if last["published_at"] else None,
    } if last else None

    cfg = await _get_ig_config(db, emp)

    return InstagramPreviewResponse(
        id_item                = item["id_item"],
        external_id            = item["external_id"],
        titulo                 = item["titulo"],
        image_url              = image_url,
        caption                = caption,
        item_activo            = item["activo"],
        instagram_configurado  = cfg is not None,
        ultima_publicacion     = ultima,
    )


# ─── Publish ─────────────────────────────────────────────────────────────────

@router.post("/publish", response_model=InstagramPublishResult)
async def publish_to_instagram(
    body: InstagramPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_admin),
):
    emp = current_user.id_empresa

    # ── Cargar item ───────────────────────────────────────────────────────────
    item_row = await db.execute(text("""
        SELECT id_item::text, titulo, activo, media
        FROM items
        WHERE id_item = :item_id AND id_empresa = :emp
    """), {"item_id": body.id_item, "emp": emp})
    item = item_row.mappings().first()
    if not item:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    # ── Validar: propiedad activa ─────────────────────────────────────────────
    if not item["activo"]:
        raise HTTPException(
            status_code=400,
            detail="Esta propiedad está inactiva. Activala en Propiedades antes de publicar en Instagram.",
        )

    # ── Validar: tiene imagen ─────────────────────────────────────────────────
    media = item["media"] or {}
    if isinstance(media, str):
        media = json.loads(media)
    image_url = _extract_image_url(media)
    if not image_url:
        raise HTTPException(
            status_code=400,
            detail="Esta propiedad no tiene imágenes. Agregá al menos una foto antes de publicar.",
        )

    # ── Validar: caption ──────────────────────────────────────────────────────
    caption = body.caption.strip()
    if not caption:
        raise HTTPException(status_code=422, detail="El caption no puede estar vacío")
    if len(caption) > _CAPTION_MAX_LEN:
        raise HTTPException(
            status_code=422,
            detail=f"El caption supera los {_CAPTION_MAX_LEN} caracteres permitidos por Instagram",
        )

    # ── Validar: config Instagram ─────────────────────────────────────────────
    cfg = await _get_ig_config(db, emp)
    if not cfg:
        raise HTTPException(
            status_code=400,
            detail="Esta empresa no tiene Instagram configurado. Configuralo en la sección Empresas.",
        )
    if cfg.get("token_expires_at"):
        expires = cfg["token_expires_at"]
        if hasattr(expires, "tzinfo"):
            if expires < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=400,
                    detail="El token de Instagram venció. Actualizalo en Configuración de Empresa.",
                )

    # ── Crear registro pending ────────────────────────────────────────────────
    post_row = await db.execute(text("""
        INSERT INTO instagram_posts
            (id_empresa, id_item, id_usuario, caption, image_url, status)
        VALUES (:emp, :item_id, :user_id, :caption, :image_url, 'pending')
        RETURNING id
    """), {
        "emp":       emp,
        "item_id":   body.id_item,
        "user_id":   current_user.id_usuario,
        "caption":   caption,
        "image_url": image_url,
    })
    post_id = post_row.scalar_one()
    await db.commit()

    # ── Llamar a Instagram Graph API ──────────────────────────────────────────
    ig_user_id   = cfg["ig_user_id"]
    access_token = cfg["access_token"]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Paso 1: crear contenedor de media
            r1 = await client.post(
                f"{_IG_API_BASE}/{ig_user_id}/media",
                params={"image_url": image_url, "caption": caption, "access_token": access_token},
            )
            r1_data = r1.json()
            if "error" in r1_data:
                raise RuntimeError(r1_data["error"].get("message", "Error al crear contenedor de media"))

            creation_id = r1_data["id"]

            # Paso 2: publicar el contenedor
            r2 = await client.post(
                f"{_IG_API_BASE}/{ig_user_id}/media_publish",
                params={"creation_id": creation_id, "access_token": access_token},
            )
            r2_data = r2.json()
            if "error" in r2_data:
                raise RuntimeError(r2_data["error"].get("message", "Error al publicar en Instagram"))

            provider_post_id = r2_data["id"]

    except Exception as exc:
        # Persistir error
        await db.execute(text("""
            UPDATE instagram_posts
               SET status = 'error', error_message = :msg
             WHERE id = :post_id
        """), {"msg": str(exc), "post_id": post_id})
        await db.commit()
        raise HTTPException(status_code=502, detail=f"Error de Instagram: {exc}")

    # ── Actualizar registro como publicado ────────────────────────────────────
    now_utc = datetime.now(timezone.utc)
    await db.execute(text("""
        UPDATE instagram_posts
           SET status = 'published',
               provider_post_id = :post_id_ig,
               published_at = :now
         WHERE id = :post_id
    """), {"post_id_ig": provider_post_id, "now": now_utc, "post_id": post_id})
    await db.commit()

    return InstagramPublishResult(
        status           = "published",
        provider_post_id = provider_post_id,
        published_at     = now_utc.isoformat(),
        error_message    = None,
    )
