from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.system import SystemOverviewResponse
from src.services.system_service import SystemService


router = APIRouter(
    prefix="/system",
    tags=["system"],
)


@router.get("/overview", response_model=SystemOverviewResponse)
def get_system_overview(
    db: Session = Depends(get_db),
) -> SystemOverviewResponse:
    """
    Return safe backend/system information for the frontend system page.
    """
    service = SystemService(db)
    return service.get_overview()