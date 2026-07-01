from src.core.config import settings
from src.storage.base import ObjectStorage
from src.storage.local_storage import LocalObjectStorage
from src.storage.s3_storage import S3ObjectStorage


def get_object_storage() -> ObjectStorage:
    """
    Create the configured object storage backend.

    STORAGE_BACKEND=local -> LocalObjectStorage
    STORAGE_BACKEND=s3    -> S3ObjectStorage
    """
    if settings.STORAGE_BACKEND == "local":
        return LocalObjectStorage(root_path=settings.LOCAL_STORAGE_PATH)

    if settings.STORAGE_BACKEND == "s3":
        return S3ObjectStorage(
            bucket_name=settings.S3_BUCKET_NAME,
            region_name=settings.AWS_REGION,
        )

    raise ValueError(f"Unsupported storage backend: {settings.STORAGE_BACKEND}")