from backend.core.logger import get_logger

logger = get_logger(__name__)

logger.info("Logger initialized successfully.")
logger.warning("This is a warning.")
logger.error("This is an error.")