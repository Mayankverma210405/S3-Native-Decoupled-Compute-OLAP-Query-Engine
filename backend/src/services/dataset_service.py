from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.database.models.dataset import Dataset
from src.database.repositories.dataset_repository import DatasetRepository
from src.schemas.dataset import DatasetCreate
from src.services.csv_analyzer import CsvAnalysisResult


class DatasetService:
    """
    Business logic for dataset operations.

    The API layer should stay thin.
    The repository layer should only handle database operations.
    This service layer sits between them and owns application rules.
    """

    def __init__(self, db: Session) -> None:
        self.repository = DatasetRepository(db)

    def register_dataset(self, payload: DatasetCreate) -> Dataset:
        """
        Register dataset metadata manually.

        For now, this creates a generated storage key.
        Later, manual registration may be removed or restricted.
        """
        s3_key = self._generate_storage_key(payload.original_filename)

        return self.repository.create_dataset(
            name=payload.name,
            original_filename=payload.original_filename,
            s3_key=s3_key,
            file_size_bytes=payload.file_size_bytes,
            row_count=payload.row_count,
            column_count=payload.column_count,
            schema_json=payload.dataset_schema,
            storage_format=payload.storage_format,
            content_type=payload.content_type,
            status="registered",
        )

    def register_analyzed_dataset(
        self,
        *,
        name: str,
        original_filename: str,
        analysis: CsvAnalysisResult,
        s3_key: str,
    ) -> Dataset:
        """
        Register a dataset using metadata extracted from a CSV file.

        The s3_key must come from the storage layer.
        This ensures the database points to the actual saved object.
        """
        return self.repository.create_dataset(
            name=name,
            original_filename=original_filename,
            s3_key=s3_key,
            file_size_bytes=analysis.file_size_bytes,
            row_count=analysis.row_count,
            column_count=analysis.column_count,
            schema_json=analysis.schema_json,
            storage_format="csv",
            content_type="text/csv",
            status="registered",
        )

    def list_datasets(self, *, limit: int = 50, offset: int = 0) -> list[Dataset]:
        return self.repository.list_datasets(limit=limit, offset=offset)

    def get_dataset_by_id(self, dataset_id: UUID) -> Dataset | None:
        return self.repository.get_dataset_by_id(dataset_id)

    def _generate_storage_key(self, original_filename: str) -> str:
        """
        Generate an object-storage-style key.

        Example:
        datasets/9fe2a1-sales.csv
        """
        safe_filename = Path(original_filename).name.replace(" ", "_")
        return f"datasets/{uuid4()}-{safe_filename}"