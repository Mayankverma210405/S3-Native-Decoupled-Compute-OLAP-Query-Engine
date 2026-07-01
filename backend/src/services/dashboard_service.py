from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.models.dataset import Dataset
from src.database.models.query_run import QueryRun
from src.storage.factory import get_object_storage


class DashboardService:
    """
    Builds high-level metrics for the application dashboard.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_summary(
        self,
        *,
        latest_runs_limit: int = 5,
    ) -> dict[str, Any]:
        """
        Return dashboard-ready aggregate metrics.
        """
        total_datasets = self.db.scalar(
            select(func.count(Dataset.id))
        ) or 0

        total_rows = self.db.scalar(
            select(func.coalesce(func.sum(Dataset.row_count), 0))
        ) or 0

        total_storage_bytes = self.db.scalar(
            select(func.coalesce(func.sum(Dataset.file_size_bytes), 0))
        ) or 0

        total_queries = self.db.scalar(
            select(func.count(QueryRun.id))
        ) or 0

        successful_queries = self.db.scalar(
            select(func.count(QueryRun.id)).where(QueryRun.status == "success")
        ) or 0

        failed_queries = self.db.scalar(
            select(func.count(QueryRun.id)).where(QueryRun.status == "failed")
        ) or 0

        average_execution_time_ms = self.db.scalar(
            select(func.avg(QueryRun.execution_time_ms)).where(
                QueryRun.execution_time_ms.is_not(None)
            )
        )

        latest_query_runs = list(
            self.db.scalars(
                select(QueryRun)
                .order_by(QueryRun.created_at.desc())
                .limit(latest_runs_limit)
            ).all()
        )

        storage = get_object_storage()

        return {
            "total_datasets": int(total_datasets),
            "total_rows": int(total_rows),
            "total_storage_bytes": int(total_storage_bytes),
            "total_storage_mb": round(int(total_storage_bytes) / (1024 * 1024), 4),
            "total_queries": int(total_queries),
            "successful_queries": int(successful_queries),
            "failed_queries": int(failed_queries),
            "average_execution_time_ms": (
                round(float(average_execution_time_ms), 2)
                if average_execution_time_ms is not None
                else None
            ),
            "storage_backend": type(storage).__name__,
            "latest_query_runs": latest_query_runs,
        }