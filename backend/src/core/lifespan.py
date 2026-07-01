from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting...")

    yield

    logger.info("Application shutting down...")