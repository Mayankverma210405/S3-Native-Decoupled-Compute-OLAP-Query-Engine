from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# Import ORM models so Alembic can discover them during migration generation.
from src.database.models import Dataset  # noqa: E402,F401