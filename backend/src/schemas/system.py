from pydantic import BaseModel


class SystemOverviewResponse(BaseModel):
    """
    Safe system overview response for the frontend.

    This intentionally does not expose secrets, access keys, or private bucket names.
    """

    project_name: str
    api_version: str
    environment: str
    debug: bool
    status: str

    storage_backend: str
    aws_region: str
    s3_configured: bool

    database_configured: bool
    total_datasets: int
    total_query_runs: int