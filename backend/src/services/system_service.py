from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.config import settings
from src.database.models.dataset import Dataset
from src.database.models.query_run import QueryRun
from src.storage.factory import get_object_storage


class SystemService:
    """
    Builds safe system-level information for the frontend.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_overview(self) -> dict[str, object]:
        total_datasets = self.db.scalar(select(func.count(Dataset.id))) or 0
        total_query_runs = self.db.scalar(select(func.count(QueryRun.id))) or 0

        storage = get_object_storage()

        return {
            "project_name": settings.PROJECT_NAME,
            "api_version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "status": "running",
            "storage_backend": type(storage).__name__,
            "aws_region": settings.AWS_REGION,
            "s3_configured": bool(settings.S3_BUCKET_NAME),
            "database_configured": bool(settings.DATABASE_URL),
            "total_datasets": int(total_datasets),
            "total_query_runs": int(total_query_runs),
        }