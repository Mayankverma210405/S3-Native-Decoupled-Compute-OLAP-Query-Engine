from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from src.core.config import settings


class S3ObjectStorage:
    """
    Amazon S3-backed object storage.

    This implementation stores dataset files in one configured private S3 bucket.
    """

    def __init__(
        self,
        *,
        bucket_name: str | None = None,
        region_name: str | None = None,
    ) -> None:
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.region_name = region_name or settings.AWS_REGION

        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME must be configured when using S3 storage")

        client_kwargs = {
            "service_name": "s3",
            "region_name": self.region_name,
        }

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        self.client = boto3.client(**client_kwargs)

    def save_file(
        self,
        *,
        source_path: str | Path,
        original_filename: str,
        prefix: str = "datasets",
    ) -> str:
        """
        Upload a local file to S3 and return the object key.

        Example:
            datasets/uuid-sales.csv
        """
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if not source.is_file():
            raise ValueError(f"Source path is not a file: {source}")

        safe_filename = self._safe_filename(original_filename)
        object_key = f"{prefix}/{uuid4()}-{safe_filename}"

        self.client.upload_file(
            Filename=str(source),
            Bucket=self.bucket_name,
            Key=object_key,
            ExtraArgs={
                "ContentType": "text/csv",
                "ServerSideEncryption": "AES256",
            },
        )

        return object_key

    def exists(self, object_key: str) -> bool:
        """
        Return True if the S3 object exists.
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            return True

        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False

            raise

    def get_read_uri(self, object_key: str) -> str:
        """
        Return an S3 URI.

        DuckDB S3 querying will use this later after we configure DuckDB's
        S3/httpfs settings.
        """
        self._validate_object_key(object_key)
        return f"s3://{self.bucket_name}/{object_key}"

    def _safe_filename(self, filename: str) -> str:
        """
        Convert user-provided filename into a safer storage filename.
        """
        cleaned = Path(filename).name.strip().replace(" ", "_")

        if not cleaned:
            raise ValueError("Filename cannot be empty")

        return cleaned

    def _validate_object_key(self, object_key: str) -> None:
        """
        Reject unsafe object keys.
        """
        key_path = Path(object_key)

        if key_path.is_absolute() or ".." in key_path.parts:
            raise ValueError(f"Unsafe object key: {object_key}")