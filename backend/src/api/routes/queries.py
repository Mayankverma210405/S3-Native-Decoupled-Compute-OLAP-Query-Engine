from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.repositories.query_run_repository import QueryRunRepository
from src.database.session import get_db
from src.schemas.query import QueryExplainResponse, QueryRequest, QueryResponse
from src.schemas.query_run import QueryRunListResponse
from src.services.query_engine import (
    DatasetNotFoundError,
    DatasetObjectNotFoundError,
    DuckDBQueryEngine,
    QueryExecutionError,
)


router = APIRouter(
    prefix="/queries",
    tags=["queries"],
)


@router.get("/runs", response_model=QueryRunListResponse)
def list_query_runs(
    dataset_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> QueryRunListResponse:
    """
    List recent query execution records.

    This powers dashboard observability and benchmark reporting.
    """
    repository = QueryRunRepository(db)
    runs = repository.list_query_runs(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )

    return QueryRunListResponse(
        items=runs,
        count=len(runs),
        limit=limit,
        offset=offset,
    )


@router.post("/execute", response_model=QueryResponse)
def execute_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Execute a read-only SQL query over one registered dataset.
    """
    query_engine = DuckDBQueryEngine(db)

    try:
        return query_engine.execute_query(
            dataset_id=payload.dataset_id,
            sql=payload.sql,
        )

    except DatasetNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except DatasetObjectNotFoundError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except QueryExecutionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/explain", response_model=QueryExplainResponse)
def explain_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryExplainResponse:
    """
    Return DuckDB's query plan for a read-only SQL query.
    """
    query_engine = DuckDBQueryEngine(db)

    try:
        return query_engine.explain_query(
            dataset_id=payload.dataset_id,
            sql=payload.sql,
        )

    except DatasetNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except DatasetObjectNotFoundError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except QueryExecutionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error