import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router
from src.core.config import settings


logger = structlog.get_logger()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
    )

    allowed_origins = [
        origin.strip()
        for origin in settings.ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "project": settings.PROJECT_NAME,
            "status": "running",
        }

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Application starting...")

    return app


app = create_app()