from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models.dataset import Dataset


class DatasetRepository:
    """
    Repository for Dataset database operations.

    This class hides raw SQLAlchemy operations from the API and service layers.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_dataset(
        self,
        *,
        name: str,
        original_filename: str,
        s3_key: str,
        file_size_bytes: int,
        row_count: int,
        column_count: int,
        schema_json: dict,
        storage_format: str = "csv",
        content_type: str = "text/csv",
        status: str = "registered",
    ) -> Dataset:
        dataset = Dataset(
            name=name,
            original_filename=original_filename,
            s3_key=s3_key,
            storage_format=storage_format,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            row_count=row_count,
            column_count=column_count,
            schema_json=schema_json,
            status=status,
        )

        try:
            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)
            return dataset
        except Exception:
            self.db.rollback()
            raise

    def get_dataset_by_id(self, dataset_id: UUID) -> Dataset | None:
        return self.db.get(Dataset, dataset_id)

    def get_dataset_by_s3_key(self, s3_key: str) -> Dataset | None:
        statement = select(Dataset).where(Dataset.s3_key == s3_key)
        return self.db.scalars(statement).first()

    def list_datasets(self, *, limit: int = 50, offset: int = 0) -> list[Dataset]:
        statement = (
            select(Dataset)
            .order_by(Dataset.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def update_dataset_status(self, dataset_id: UUID, status: str) -> Dataset | None:
        dataset = self.get_dataset_by_id(dataset_id)

        if dataset is None:
            return None

        dataset.status = status

        try:
            self.db.commit()
            self.db.refresh(dataset)
            return dataset
        except Exception:
            self.db.rollback()
            raise