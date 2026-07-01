from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.dataset import (
    DatasetCreate,
    DatasetDownloadUrlResponse,
    DatasetListResponse,
    DatasetPreviewResponse,
    DatasetRead,
)
from src.services.csv_analyzer import CsvAnalyzer
from src.services.dataset_service import DatasetService
from src.services.query_engine import (
    DatasetNotFoundError,
    DatasetObjectNotFoundError,
    DuckDBQueryEngine,
    QueryExecutionError,
)
from src.storage.factory import get_object_storage


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
    Upload a CSV file, analyze it, store it, and register dataset metadata.
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


@router.get("/{dataset_id}/download-url", response_model=DatasetDownloadUrlResponse)
def get_dataset_download_url(
    dataset_id: UUID,
    expires_in_seconds: int = Query(default=900, ge=60, le=3600),
    db: Session = Depends(get_db),
) -> DatasetDownloadUrlResponse:
    """
    Generate a temporary download URL for the raw dataset object.

    For S3 storage, this returns a presigned S3 URL.
    For local storage, this returns a local file URI for development.
    """
    service = DatasetService(db)
    dataset = service.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    storage = get_object_storage()

    if not storage.exists(dataset.s3_key):
        raise HTTPException(
            status_code=409,
            detail=f"Dataset object not found for key: {dataset.s3_key}",
        )

    try:
        download_url = storage.generate_download_url(
            dataset.s3_key,
            expires_in_seconds=expires_in_seconds,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate download URL: {error}",
        ) from error

    return DatasetDownloadUrlResponse(
        dataset_id=dataset.id,
        object_key=dataset.s3_key,
        download_url=download_url,
        expires_in_seconds=expires_in_seconds,
        storage_backend=type(storage).__name__,
    )


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Fetch a single dataset by ID.
    """
    service = DatasetService(db)
    dataset = service.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return dataset