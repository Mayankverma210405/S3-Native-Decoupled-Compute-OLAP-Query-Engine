from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.dashboard import DashboardSummaryResponse
from src.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    latest_runs_limit: int = Query(default=5, ge=0, le=20),
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    """
    Return high-level metrics for the engineering dashboard.
    """
    service = DashboardService(db)

    return service.get_summary(
        latest_runs_limit=latest_runs_limit,
    )