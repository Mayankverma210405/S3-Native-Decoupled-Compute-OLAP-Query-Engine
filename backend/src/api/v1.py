from fastapi import APIRouter

from src.api.health import router as health_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.datasets import router as datasets_router
from src.api.routes.queries import router as queries_router
from src.api.routes.system import router as system_router


router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(dashboard_router)
router.include_router(datasets_router)
router.include_router(queries_router)
router.include_router(system_router)