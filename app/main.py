"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routes import health


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup and shutdown events for the application."""
    # TODO: add startup logic (db connections, caches, etc.)
    yield
    # TODO: add shutdown cleanup here


def create_app() -> FastAPI:
    """Application factory."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    @application.get("/")
    async def root() -> dict:
        """Root endpoint for load balancers and quick sanity checks."""
        return {"status": "ok"}

    application.include_router(
        health.router,
        prefix=settings.api_prefix,
    )

    return application


app = create_app()
