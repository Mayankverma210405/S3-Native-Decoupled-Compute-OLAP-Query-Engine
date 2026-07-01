from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models.query_run import QueryRun


class QueryRunRepository:
    """
    Persistence layer for query execution history.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_query_run(
        self,
        *,
        dataset_id: UUID,
        sql_text: str,
        status: str,
        storage_backend: str,
        row_count: int = 0,
        execution_time_ms: float | None = None,
        error_message: str | None = None,
    ) -> QueryRun:
        query_run = QueryRun(
            dataset_id=dataset_id,
            sql_text=sql_text,
            status=status,
            storage_backend=storage_backend,
            row_count=row_count,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
        )

        self.db.add(query_run)
        self.db.commit()
        self.db.refresh(query_run)

        return query_run

    def list_query_runs(
        self,
        *,
        dataset_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[QueryRun]:
        statement = select(QueryRun).order_by(QueryRun.created_at.desc())

        if dataset_id is not None:
            statement = statement.where(QueryRun.dataset_id == dataset_id)

        statement = statement.limit(limit).offset(offset)

        return list(self.db.scalars(statement).all())