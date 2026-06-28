from fastapi import APIRouter

from src.api.health import router as health_router
from src.api.routes.datasets import router as datasets_router


router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(datasets_router)