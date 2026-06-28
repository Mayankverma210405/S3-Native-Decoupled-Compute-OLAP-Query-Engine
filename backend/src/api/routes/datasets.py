from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.dataset import (
    DatasetCreate,
    DatasetListResponse,
    DatasetPreviewResponse,
    DatasetRead,
)
from src.services.csv_analyzer import CsvAnalyzer
from src.services.dataset_service import DatasetService
from src.storage.factory import get_object_storage
from src.services.query_engine import (
    DatasetNotFoundError,
    DatasetObjectNotFoundError,
    DuckDBQueryEngine,
    QueryExecutionError,
)

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
)


@router.post(
    "/upload",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Upload a CSV file, analyze it, and register dataset metadata.

    In this version, we analyze the CSV and store metadata in PostgreSQL.
    S3 upload will be added in the next storage module.
    """
    original_filename = Path(file.filename or "").name

    if not original_filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename",
        )

    if Path(original_filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported",
        )

    temp_path: Path | None = None

    try:
        with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = Path(temp_file.name)

            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)

        analyzer = CsvAnalyzer()
        analysis = analyzer.analyze(temp_path)

        storage = get_object_storage()
        object_key = storage.save_file(
            source_path=temp_path,
            original_filename=original_filename,
        )

        dataset_name = name or Path(original_filename).stem

        service = DatasetService(db)
        return service.register_analyzed_dataset(
            name=dataset_name,
            original_filename=original_filename,
            analysis=analysis,
            s3_key=object_key,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    finally:
        await file.close()

        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


@router.post(
    "",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
def register_dataset(
    payload: DatasetCreate,
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Register dataset metadata manually.

    This is useful for development and testing.
    Full CSV upload uses /datasets/upload.
    """
    service = DatasetService(db)
    return service.register_dataset(payload)


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
    service = DatasetService(db)
    datasets = service.list_datasets(limit=limit, offset=offset)

    return DatasetListResponse(
        items=datasets,
        count=len(datasets),
        limit=limit,
        offset=offset,
    )
@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(
    dataset_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> DatasetPreviewResponse:
    """
    Preview the first rows of a dataset.

    This is useful for frontend dashboards before users write SQL manually.
    """
    query_engine = DuckDBQueryEngine(db)

    try:
        return query_engine.preview_dataset(
            dataset_id=dataset_id,
            limit=limit,
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

@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Fetch a single dataset by ID.

    This endpoint will be used for dataset detail pages and query execution.
    """
    service = DatasetService(db)
    dataset = service.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return dataset