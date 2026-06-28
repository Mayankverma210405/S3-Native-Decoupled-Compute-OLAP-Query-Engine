from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QueryRunRead(BaseModel):
    """
    Response schema for a single query execution record.
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


class QueryRunListResponse(BaseModel):
    """
    Response schema for listing query execution records.
    """

    items: list[QueryRunRead]
    count: int
    limit: int
    offset: int