from datetime import datetime, timezone
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Dataset(Base):
    """
    Metadata catalog entry for a dataset stored in object storage.

    This table does not store the actual CSV file.
    The CSV file will live in S3.
    PostgreSQL stores searchable metadata about that file.
    """

    __tablename__ = "datasets"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    s3_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
        index=True,
    )

    storage_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="csv",
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="text/csv",
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    row_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    schema_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="registered",
    )

    query_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_query_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "storage_format IN ('csv')",
            name="ck_datasets_storage_format_csv",
        ),
        CheckConstraint(
            "status IN ('registered', 'uploading', 'uploaded', 'failed', 'deleted')",
            name="ck_datasets_status_valid",
        ),
        Index("ix_datasets_created_at", "created_at"),
    )