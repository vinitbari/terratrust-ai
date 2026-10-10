"""FIN-03 FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown routines."""
    # Startup: configure logging
    setup_logging(log_level=settings.LOG_LEVEL)

    # Auto-initialize database tables and seed sample data for zero-config deployment
    try:
        from app.models.base import Base
        from app.db.session import engine, SessionLocal
        from app.db.seed import seed_database
        import app.models  # noqa: F401 - Register all models
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db_session:
            seed_database(db_session)
            db_session.commit()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Database auto-initialization skipped/failed: %s", exc)

    yield
    # Shutdown routines if any


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="FIN-03 Agricultural Climate-Aware Credit Risk API",
        version="1.0.0",
        description="Decision-support system for climate-aware agricultural credit risk assessment.",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        lifespan=lifespan,
    )

    # Middleware: Request ID and correlation
    app.add_middleware(RequestIdMiddleware)

    # Middleware: CORS (Allows local and cloud/custom domains)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"^https?://.*$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
    )

    # Exception Handlers conforming to error envelope schema
    register_error_handlers(app)

    # ML Crop Yield Prediction Router (TerraTrust Model)
    from app.api.v1.endpoints.predict_yield import router as predict_router
    app.include_router(predict_router)
    app.include_router(predict_router, prefix="/api/v1")

    # Router Mounting
    app.include_router(api_v1_router, prefix="/api/v1")

    # Convenience root health check
    @app.get("/health", tags=["Health"], include_in_schema=False)
    def root_health():
        return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}

    # Redirect /docs to /api/v1/docs
    @app.get("/docs", include_in_schema=False)
    def docs_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/api/v1/docs")

    # Serve Frontend Single Page App if built (unified deployment support)
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    dist_dir = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
    if not dist_dir.exists():
        dist_dir = Path(__file__).resolve().parent.parent / "dist"

    if dist_dir.exists() and (dist_dir / "index.html").exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            if full_path.startswith("api/") or full_path == "predict-yield" or full_path.startswith("predict-yield"):
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Not Found")
            target = dist_dir / full_path
            if target.is_file():
                return FileResponse(target)
            return FileResponse(dist_dir / "index.html")

    return app


app = create_app()
