from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Request schema for executing SQL against a dataset.

    The dataset is exposed inside DuckDB as a table named 'dataset'.
    """

    dataset_id: UUID
    sql: str = Field(min_length=1, max_length=10_000)


class QueryResponse(BaseModel):
    """
    Response schema for query execution results.
    """

    dataset_id: UUID
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: float


class QueryExplainResponse(BaseModel):
    """
    Response schema for DuckDB query plans.
    """

    dataset_id: UUID
    sql: str
    plan: list[dict[str, Any]]
    plan_text: str
    execution_time_ms: float