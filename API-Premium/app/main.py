from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.logging import get_logger, setup_logging
from app.models.api_models import HealthResponse
from app.routers import admin_auth, admin_empresas, admin_items, admin_leads, analytics, catalogo, chat, leads, webhook_widget, webhook_whatsapp

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("inmobot_premium_starting", version="0.1.0")
    yield
    await engine.dispose()
    logger.info("inmobot_premium_stopped")


app = FastAPI(
    title="InmoBot Premium API",
    description="Backend conversacional multi-tenant para agentes de IA inmobiliarios.",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins != ["*"] else ["*"],
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth.router,        prefix="/admin/auth",      tags=["admin"])
app.include_router(admin_empresas.router,    prefix="/admin/empresas",  tags=["admin"])
app.include_router(admin_leads.router,       prefix="/admin/leads",     tags=["admin"])
app.include_router(admin_items.router,       prefix="/admin/items",     tags=["admin"])
app.include_router(chat.router,              prefix="/chat",      tags=["chat"])
app.include_router(webhook_widget.router,    prefix="/webhook",   tags=["webhooks"])
app.include_router(webhook_whatsapp.router,  prefix="/webhook",   tags=["webhooks"])
app.include_router(catalogo.router,          prefix="/catalogo",  tags=["catálogo"])
app.include_router(leads.router,             prefix="/leads",     tags=["leads"])
app.include_router(analytics.router,         prefix="/analytics", tags=["analytics"])


@app.get("/health", response_model=HealthResponse, tags=["sistema"])
async def health_check() -> HealthResponse:
    db_status = "ok"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(status="ok", version="0.1.0", db=db_status)
