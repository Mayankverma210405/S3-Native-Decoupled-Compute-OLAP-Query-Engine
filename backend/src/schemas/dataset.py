from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    """
    Request schema for registering dataset metadata.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    original_filename: str = Field(min_length=1, max_length=255)
    storage_format: str = "csv"
    content_type: str = "text/csv"
    file_size_bytes: int = Field(ge=0)
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    dataset_schema: dict[str, Any] = Field(alias="schema_json")


class DatasetRead(BaseModel):
    """
    Response schema for a dataset.
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


class DatasetPreviewResponse(BaseModel):
    """
    Response schema for previewing dataset rows.
    """

    dataset_id: UUID
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    limit: int
    execution_time_ms: float


class DatasetDownloadUrlResponse(BaseModel):
    """
    Response schema for temporary dataset download URLs.
    """

    dataset_id: UUID
    object_key: str
    download_url: str
    expires_in_seconds: int
    storage_backend: str


class DatasetListResponse(BaseModel):
    """
    Response schema for listing datasets.
    """

    items: list[DatasetRead]
    count: int
    limit: int
    offset: int