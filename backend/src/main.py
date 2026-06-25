from fastapi import FastAPI

from src.api.v1 import router
from src.core.config import settings
from src.core.lifespan import lifespan

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
    }