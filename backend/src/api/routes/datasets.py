from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.repositories.dataset_repository import DatasetRepository
from src.database.session import get_db
from src.schemas.dataset import DatasetListResponse, DatasetRead


router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
)


@router.get("", response_model=DatasetListResponse)
def list_datasets(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> DatasetListResponse:
    """
    List registered datasets.

    This endpoint will be used by the dashboard to show available datasets.
    """
    repository = DatasetRepository(db)
    datasets = repository.list_datasets(limit=limit, offset=offset)

    return DatasetListResponse(
        items=datasets,
        count=len(datasets),
        limit=limit,
        offset=offset,
    )


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Fetch a single dataset by ID.

    This endpoint will be used for dataset detail pages and query execution.
    """
    repository = DatasetRepository(db)
    dataset = repository.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return dataset