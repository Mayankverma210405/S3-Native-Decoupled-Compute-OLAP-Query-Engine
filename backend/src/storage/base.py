from pathlib import Path
from typing import Protocol


class ObjectStorage(Protocol):
    """
    Common interface for object storage backends.

    Local storage and S3 storage should both follow this contract.
    """

    def save_file(
        self,
        *,
        source_path: str | Path,
        original_filename: str,
        prefix: str = "datasets",
    ) -> str:
        """
        Save a file and return an object key.
        """
        ...

    def exists(self, object_key: str) -> bool:
        """
        Return True if the object exists.
        """
        ...

    def get_read_uri(self, object_key: str) -> str:
        """
        Return a URI/path that DuckDB can read.
        """
        ...

    def generate_download_url(
        self,
        object_key: str,
        expires_in_seconds: int = 900,
    ) -> str:
        """
        Generate a temporary URL/path for downloading an object.
        """
        ...