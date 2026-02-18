"""ConektaBots — FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-5s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("conekta-bots")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: startup e shutdown da aplicação."""
    # Startup
    logger.info("🚀 ConektaBots API iniciando...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database pronta")
    yield
    # Shutdown
    logger.info("👋 ConektaBots API encerrando...")


app = FastAPI(
    title=settings.APP_NAME,
    description="API para gerenciamento de bots Telegram com regras de encaminhamento e agendamentos.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers globais
register_exception_handlers(app)

# API v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
