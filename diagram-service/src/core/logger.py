import sys
from pathlib import Path
from loguru import logger
from src.core.config import settings


def setup_logger():
    logger.remove()
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if settings.log_format == "json":
        logger.add(
            sys.stderr,
            format="{message}",
            level=settings.log_level,
            serialize=True,
        )
    else:
        logger.add(
            sys.stderr,
            format=log_format,
            level=settings.log_level,
            colorize=True,
        )
    
    log_file_path = Path(settings.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.log_file,
        rotation="100 MB",
        retention="10 days",
        compression="zip",
        format=log_format,
        level=settings.log_level,
        serialize=settings.log_format == "json",
    )
    
    return logger


app_logger = setup_logger()
