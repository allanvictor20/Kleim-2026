"""FastAPI application factory (M0). Routers are registered here as modules are built."""
from fastapi import FastAPI

app = FastAPI(title="Kleim API", version="0.1.0", docs_url="/docs")


@app.get("/health/live", tags=["Health"])
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def ready() -> dict[str, str]:
    # M0: check database and Redis connectivity here.
    return {"status": "ok"}


# Register module routers under /api/v1 as each module is implemented, e.g.:
# from app.identity.router import router as identity_router
# app.include_router(identity_router, prefix="/api/v1")
