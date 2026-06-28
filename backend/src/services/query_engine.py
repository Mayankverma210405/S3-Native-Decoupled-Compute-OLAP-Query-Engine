import re
import time
from typing import Any
from uuid import UUID

import duckdb
from sqlalchemy.orm import Session

from src.core.config import settings
from src.database.repositories.dataset_repository import DatasetRepository
from src.database.repositories.query_run_repository import QueryRunRepository
from src.storage.base import ObjectStorage
from src.storage.factory import get_object_storage



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
        storage: ObjectStorage | None = None,
    ) -> None:
        self.dataset_repository = DatasetRepository(db)
        self.query_run_repository = QueryRunRepository(db)
        self.storage = storage or get_object_storage()

    def execute_query(
        self,
        *,
        dataset_id: UUID,
        sql: str,
    ) -> dict[str, Any]:
        """
        Execute a read-only SQL query against one dataset.
        """
        dataset, read_uri, safe_sql = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql=sql,
        )

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._configure_duckdb_storage(connection, read_uri)
                self._register_csv_as_dataset_table(connection, read_uri)

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

        self.query_run_repository.create_query_run(
            dataset_id=dataset.id,
            sql_text=safe_sql,
            status="success",
            storage_backend=type(self.storage).__name__,
            row_count=len(rows),
            execution_time_ms=execution_time_ms,
        )

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

        dataset, read_uri, _ = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql="SELECT * FROM dataset",
        )

        sql = f"SELECT * FROM dataset LIMIT {limit}"

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._configure_duckdb_storage(connection, read_uri)
                self._register_csv_as_dataset_table(connection, read_uri)

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
        dataset, read_uri, safe_sql = self._prepare_dataset_query(
            dataset_id=dataset_id,
            sql=sql,
        )

        started_at = time.perf_counter()

        try:
            with duckdb.connect(database=":memory:") as connection:
                self._configure_duckdb_storage(connection, read_uri)
                self._register_csv_as_dataset_table(connection, read_uri)

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
    ) -> tuple[Any, str, str]:
        """
        Validate dataset existence, object existence, and SQL safety.
        """
        dataset = self.dataset_repository.get_dataset_by_id(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError(f"Dataset not found: {dataset_id}")

        if not self.storage.exists(dataset.s3_key):
            raise DatasetObjectNotFoundError(
                f"Dataset object not found for key: {dataset.s3_key}"
            )

        read_uri = self.storage.get_read_uri(dataset.s3_key)
        safe_sql = self._validate_and_normalize_sql(sql)

        return dataset, read_uri, safe_sql

    def _configure_duckdb_storage(
        self,
        connection: duckdb.DuckDBPyConnection,
        read_uri: str,
    ) -> None:
        """
        Configure DuckDB for the storage backend used by the dataset.

        Local files do not need extra configuration.
        S3 files need DuckDB's httpfs extension and S3 credentials.
        """
        if not read_uri.startswith("s3://"):
            return

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise QueryExecutionError(
                "AWS credentials are required for DuckDB S3 reads"
            )

        connection.execute("INSTALL httpfs")
        connection.execute("LOAD httpfs")

        key_id = self._quote_duckdb_string(settings.AWS_ACCESS_KEY_ID)
        secret = self._quote_duckdb_string(settings.AWS_SECRET_ACCESS_KEY)
        region = self._quote_duckdb_string(settings.AWS_REGION)
        endpoint = self._quote_duckdb_string(f"s3.{settings.AWS_REGION}.amazonaws.com")

        connection.execute(
            f"""
            CREATE OR REPLACE SECRET s3_query_secret (
                TYPE s3,
                PROVIDER config,
                KEY_ID '{key_id}',
                SECRET '{secret}',
                REGION '{region}',
                ENDPOINT '{endpoint}'
            )
            """
        )

    def _register_csv_as_dataset_table(
        self,
        connection: duckdb.DuckDBPyConnection,
        read_uri: str,
    ) -> None:
        """
        Register the stored CSV file as a DuckDB view named 'dataset'.
        """
        escaped_uri = self._quote_duckdb_string(read_uri)

        connection.execute(
            f"""
            CREATE VIEW dataset AS
            SELECT *
            FROM read_csv_auto('{escaped_uri}', header = true)
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

    def _quote_duckdb_string(self, value: str) -> str:
        """
        Escape single quotes before interpolating into DuckDB SQL strings.
        """
        return value.replace("'", "''")