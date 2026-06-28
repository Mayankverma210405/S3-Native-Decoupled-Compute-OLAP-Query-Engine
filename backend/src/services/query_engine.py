import re
import time
from pathlib import Path
from typing import Any
from uuid import UUID

import duckdb
from sqlalchemy.orm import Session

from src.database.repositories.dataset_repository import DatasetRepository
from src.storage.local_storage import LocalObjectStorage


class QueryExecutionError(Exception):
    """Raised when a query cannot be executed safely or correctly."""


class DatasetNotFoundError(Exception):
    """Raised when the requested dataset does not exist."""


class DatasetObjectNotFoundError(Exception):
    """Raised when dataset metadata exists but the stored file is missing."""


class DuckDBQueryEngine:
    """
    Execute SQL queries over stored CSV datasets using DuckDB.

    For v1, every uploaded dataset is exposed to SQL as a table named:

        dataset

    Example:

        SELECT * FROM dataset LIMIT 10;
    """

    def __init__(
        self,
        db: Session,
        storage: LocalObjectStorage | None = None,
    ) -> None:
        self.dataset_repository = DatasetRepository(db)
        self.storage = storage or LocalObjectStorage()

    def execute_query(
        self,
        *,
        dataset_id: UUID,
        sql: str,
    ) -> dict[str, Any]:
        """
        Execute a read-only SQL query against one dataset.
        """
        dataset, object_path, safe_sql = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql=sql,
        )

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._register_csv_as_dataset_table(connection, object_path)

                result = connection.execute(safe_sql)
                columns = [description[0] for description in result.description]
                raw_rows = result.fetchall()

        except duckdb.Error as error:
            raise QueryExecutionError(str(error)) from error

        execution_time_ms = round((time.perf_counter() - started_at) * 1000, 2)

        rows = [
            {column: value for column, value in zip(columns, row, strict=False)}
            for row in raw_rows
        ]

        self.dataset_repository.mark_dataset_queried(dataset.id)

        return {
            "dataset_id": dataset.id,
            "sql": safe_sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": execution_time_ms,
        }
        
    def preview_dataset(
        self,
        *,
        dataset_id: UUID,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Return a small preview of dataset rows.

        Preview is useful for dashboards and does not increment query_count.
        """
        if limit < 1 or limit > 100:
            raise QueryExecutionError("Preview limit must be between 1 and 100")

        dataset, object_path, _ = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql="SELECT * FROM dataset",
        )

        sql = f"SELECT * FROM dataset LIMIT {limit}"

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._register_csv_as_dataset_table(connection, object_path)

                result = connection.execute(sql)
                columns = [description[0] for description in result.description]
                raw_rows = result.fetchall()

        except duckdb.Error as error:
            raise QueryExecutionError(str(error)) from error

        execution_time_ms = round((time.perf_counter() - started_at) * 1000, 2)

        rows = [
            {column: value for column, value in zip(columns, row, strict=False)}
            for row in raw_rows
        ]

        return {
            "dataset_id": dataset.id,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "limit": limit,
            "execution_time_ms": execution_time_ms,
        }

    def explain_query(
        self,
        *,
        dataset_id: UUID,
        sql: str,
    ) -> dict[str, Any]:
        """
        Return DuckDB's query plan for a read-only SQL query.

        EXPLAIN does not count as a dataset query execution because it does
        not return the query result rows to the user.
        """
        dataset, object_path, safe_sql = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql=sql,
        )

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._register_csv_as_dataset_table(connection, object_path)

                result = connection.execute(f"EXPLAIN {safe_sql}")
                columns = [description[0] for description in result.description]
                raw_rows = result.fetchall()

        except duckdb.Error as error:
            raise QueryExecutionError(str(error)) from error

        execution_time_ms = round((time.perf_counter() - started_at) * 1000, 2)

        plan_rows = [
            {column: value for column, value in zip(columns, row, strict=False)}
            for row in raw_rows
        ]

        plan_text = "\n".join(
            " | ".join(str(value) for value in row if value is not None)
            for row in raw_rows
        )

        return {
            "dataset_id": dataset.id,
            "sql": safe_sql,
            "plan": plan_rows,
            "plan_text": plan_text,
            "execution_time_ms": execution_time_ms,
        }

    def _prepare_dataset_query(
        self,
        *,
        dataset_id: UUID,
        sql: str,
    ) -> tuple[Any, Path, str]:
        """
        Validate dataset existence, file existence, and SQL safety.
        """
        dataset = self.dataset_repository.get_dataset_by_id(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError(f"Dataset not found: {dataset_id}")

        object_path = self.storage.get_path(dataset.s3_key)

        if not object_path.exists():
            raise DatasetObjectNotFoundError(
                f"Dataset object not found for key: {dataset.s3_key}"
            )

        safe_sql = self._validate_and_normalize_sql(sql)

        return dataset, object_path, safe_sql

    def _register_csv_as_dataset_table(
        self,
        connection: duckdb.DuckDBPyConnection,
        object_path: Path,
    ) -> None:
        """
        Register the stored CSV file as a DuckDB view named 'dataset'.
        """
        csv_path = object_path.resolve().as_posix().replace("'", "''")

        connection.execute(
            f"""
            CREATE VIEW dataset AS
            SELECT *
            FROM read_csv_auto('{csv_path}', header = true)
            """
        )

    def _validate_and_normalize_sql(self, sql: str) -> str:
        """
        Keep v1 query execution read-only.

        This is not a full SQL sandbox yet, but it prevents obvious destructive
        or filesystem-related statements.
        """
        normalized_sql = sql.strip().rstrip(";").strip()

        if not normalized_sql:
            raise QueryExecutionError("SQL query cannot be empty")

        lowered_sql = normalized_sql.lower()

        allowed_starts = ("select", "with")

        if not lowered_sql.startswith(allowed_starts):
            raise QueryExecutionError("Only SELECT queries are allowed in v1")

        forbidden_keywords = {
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "create",
            "copy",
            "attach",
            "install",
            "load",
            "export",
            "pragma",
            "set",
            "call",
        }

        for keyword in forbidden_keywords:
            if re.search(rf"\b{keyword}\b", lowered_sql):
                raise QueryExecutionError(
                    f"Keyword not allowed in v1 query: {keyword}"
                )

        if ";" in normalized_sql:
            raise QueryExecutionError("Multiple SQL statements are not allowed")

        return normalized_sql