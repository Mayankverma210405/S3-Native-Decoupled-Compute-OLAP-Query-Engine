import shutil
from pathlib import Path
from uuid import uuid4


class LocalObjectStorage:
    """
    Local filesystem-backed object storage.

    This mimics S3-style object storage during local development.
    """

    def __init__(self, root_path: str | Path = "storage") -> None:
        self.root_path = Path(root_path)

    def save_file(
        self,
        *,
        source_path: str | Path,
        original_filename: str,
        prefix: str = "datasets",
    ) -> str:
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if not source.is_file():
            raise ValueError(f"Source path is not a file: {source}")

        safe_filename = self._safe_filename(original_filename)
        object_key = f"{prefix}/{uuid4()}-{safe_filename}"

        destination = self._resolve_key(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination)

        return object_key

    def exists(self, object_key: str) -> bool:
        return self._resolve_key(object_key).exists()

    def get_path(self, object_key: str) -> Path:
        return self._resolve_key(object_key)

    def get_read_uri(self, object_key: str) -> str:
        return self.get_path(object_key).resolve().as_posix()

    def generate_download_url(
        self,
        object_key: str,
        expires_in_seconds: int = 900,
    ) -> str:
        """
        Return a local file URI for development.

        The expiry value is ignored for local storage.
        """
        if not self.exists(object_key):
            raise FileNotFoundError(f"Object not found: {object_key}")

        return self.get_path(object_key).resolve().as_uri()

    def _safe_filename(self, filename: str) -> str:
        cleaned = Path(filename).name.strip().replace(" ", "_")

        if not cleaned:
            raise ValueError("Filename cannot be empty")

        return cleaned

    def _resolve_key(self, object_key: str) -> Path:
        key_path = Path(object_key)

        if key_path.is_absolute() or ".." in key_path.parts:
            raise ValueError(f"Unsafe object key: {object_key}")

        return self.root_path / key_path