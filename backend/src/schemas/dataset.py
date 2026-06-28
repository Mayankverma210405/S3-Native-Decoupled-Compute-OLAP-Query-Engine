from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetRead(BaseModel):
    """
    Response schema for a dataset.

    This is what the API sends to the frontend/client.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    name: str
    original_filename: str
    s3_key: str
    storage_format: str
    content_type: str
    file_size_bytes: int
    row_count: int
    column_count: int
    dataset_schema: dict[str, Any] = Field(alias="schema_json")
    status: str
    query_count: int
    last_query_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DatasetListResponse(BaseModel):
    """
    Response schema for listing datasets.

    We wrap the list with metadata so the frontend can support pagination later.
    """

    items: list[DatasetRead]
    count: int
    limit: int
    offset: int