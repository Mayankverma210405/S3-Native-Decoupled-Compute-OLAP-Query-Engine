from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    """
    Basic API health check.
    """
    return {
        "status": "ok",
        "service": "S3 Native Decoupled Compute OLAP Query Engine",
    }