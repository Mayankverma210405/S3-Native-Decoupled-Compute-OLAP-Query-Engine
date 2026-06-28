from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LatestQueryRunSummary(BaseModel):
    """
    Compact query run record for dashboard display.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dataset_id: UUID
    sql_text: str
    status: str
    storage_backend: str
    row_count: int
    execution_time_ms: float | None
    error_message: str | None
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    """
    High-level system metrics for the dashboard.
    """

    total_datasets: int
    total_rows: int
    total_storage_bytes: int
    total_storage_mb: float
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_execution_time_ms: float | None
    storage_backend: str
    latest_query_runs: list[LatestQueryRunSummary]