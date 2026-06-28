from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.query import QueryRequest, QueryResponse
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


@router.post(
    "/execute",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
def execute_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Execute a SQL query over a registered dataset.

    The target CSV is exposed to DuckDB as a table named 'dataset'.
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