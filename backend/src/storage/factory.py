from src.core.config import settings
from src.storage.base import ObjectStorage
from src.storage.local_storage import LocalObjectStorage


def get_object_storage() -> ObjectStorage:
    """
    Create the configured object storage backend.

    For now, only local storage is implemented.
    Later, this factory will return S3ObjectStorage when STORAGE_BACKEND=s3.
    """
    if settings.STORAGE_BACKEND == "local":
        return LocalObjectStorage(root_path=settings.LOCAL_STORAGE_PATH)

    raise ValueError(f"Unsupported storage backend: {settings.STORAGE_BACKEND}")