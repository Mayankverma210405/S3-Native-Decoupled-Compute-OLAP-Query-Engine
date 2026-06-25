import logging
import structlog

from src.core.config import settings


logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(message)s",
)

logger = structlog.get_logger()