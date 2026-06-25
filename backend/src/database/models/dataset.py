from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    s3_key: Mapped[str] = mapped_column(
        String(1024),
        unique=True,
        nullable=False,
    )

    storage_format: Mapped[str] = mapped_column(
        String(20),
        default="csv",
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        default="text/csv",
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    row_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    column_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    query_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="uploaded",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    last_query_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )