"""ContribHub API — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import auth, health, issues, matches, repos, triage, webhooks
from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.workers.health_worker import start_health_scheduler

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown resources."""
    logger.info("Starting %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)

    # Startup
    await init_db()
    logger.info("Database connection verified")

    scheduler = None
    try:
        scheduler = start_health_scheduler()
    except Exception:
        logger.warning("Health scheduler could not start — continuing without it")

    yield

    # Shutdown
    if scheduler:
        scheduler.shutdown(wait=False)
    await close_db()
    logger.info("Shutdown complete")


# ── Application ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "ContribHub — AI-powered GitHub issue triage and contributor matching. "
        "Automatically classify, prioritize, and route open-source issues to the "
        "right contributors."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router mounting ──────────────────────────────────────────────────────────
api_v1_prefix = "/api/v1"

app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(repos.router, prefix=api_v1_prefix)
app.include_router(issues.router, prefix=api_v1_prefix)
app.include_router(matches.router, prefix=api_v1_prefix)
app.include_router(triage.router, prefix=api_v1_prefix)
app.include_router(webhooks.router, prefix=api_v1_prefix)
app.include_router(health.router, prefix=api_v1_prefix)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }
