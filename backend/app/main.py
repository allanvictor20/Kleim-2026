"""FastAPI application factory (M0). Routers are registered here as modules are built."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.db import check_database, dispose_engine
from app.core.errors import error_body, register_exception_handlers
from app.core.idempotency import HEADER as IDEMPOTENCY_HEADER
from app.core.idempotency import IdempotencyMiddleware
from app.core.logging import configure_logging, init_sentry
from app.core.middleware import HEADER as REQUEST_ID_HEADER
from app.core.middleware import RequestIdMiddleware
from app.core.redis import check_redis, close_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    logger.info("starting api", extra={"environment": settings.app_env})
    yield
    await close_redis()
    dispose_engine()


def register_health_routes(app: FastAPI) -> None:
    @app.get("/health/live", tags=["Health"])
    def live() -> dict[str, str]:
        """Liveness: the process is running. Deliberately checks nothing else,
        so a database blip does not get the container restarted."""
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Health"])
    async def ready() -> JSONResponse:
        """Readiness: refuse traffic unless the database and Redis both answer."""
        checks: dict[str, str] = {}

        try:
            check_database()
            checks["database"] = "ok"
        except Exception:
            logger.exception("readiness: database unreachable")
            checks["database"] = "unavailable"

        try:
            await check_redis()
            checks["redis"] = "ok"
        except Exception:
            logger.exception("readiness: redis unreachable")
            checks["redis"] = "unavailable"

        if all(state == "ok" for state in checks.values()):
            return JSONResponse(content={"status": "ok", "checks": checks})

        body = error_body(
            "SERVICE_UNAVAILABLE",
            "A dependency is unavailable",
            {"checks": checks},
        )
        return JSONResponse(status_code=503, content=body)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    init_sentry(settings)

    app = FastAPI(title="Kleim API", version="0.1.0", docs_url="/docs", lifespan=lifespan)
    app.state.settings = settings

    # Starlette runs the most recently added middleware outermost, so the
    # request id is set before idempotency can replay a cached response and is
    # therefore present on every log line and error body. CORS goes outermost of
    # all: a preflight must be answered even when a later layer would reject the
    # request, or the browser reports a CORS failure instead of the real error.
    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", IDEMPOTENCY_HEADER, REQUEST_ID_HEADER],
        # Without this the browser hides the header, and a bug report loses the
        # one id that ties it to a backend log line.
        expose_headers=[REQUEST_ID_HEADER],
        max_age=600,
    )

    register_exception_handlers(app)
    register_health_routes(app)

    # Register module routers under /api/v1 as each module is implemented, e.g.:
    # from app.identity.router import router as identity_router
    # app.include_router(identity_router, prefix="/api/v1")
    return app


app = create_app()
