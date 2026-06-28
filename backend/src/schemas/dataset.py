from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    """
    Request schema for registering dataset metadata.

    Later, CSV upload code will generate this metadata automatically.
    For now, we send it manually to test the backend flow.
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