from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


# Import all ORM models so Alembic can discover them.
from src.database.models import Dataset  # noqa: E402,F401