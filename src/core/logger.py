"""
Logging configuration module
"""
import sys
from pathlib import Path
from loguru import logger
from src.core.config import settings


def setup_logger():
    """Setup logger with appropriate configuration"""
    
    # Remove default handler
    logger.remove()
    
    # Determine log level
    log_level = settings.log_level.upper()
    
    # Console handler with color
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if settings.is_debug:
        # Debug mode: more verbose
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level> | "
            "<yellow>{extra}</yellow>"
        )
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True,
        backtrace=settings.is_debug,
        diagnose=settings.is_debug,
    )
    
    # File handler for all logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logger.add(
        logs_dir / "remnabot_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG" if settings.is_debug else "INFO",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated logs
        backtrace=True,
        diagnose=True,
    )
    
    # Separate file for errors
    logger.add(
        logs_dir / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="00:00",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    logger.info(f"Logger initialized with level: {log_level}")
    if settings.is_debug:
        logger.debug("Debug mode enabled - verbose logging active")
    
    return logger


# Initialize logger
log = setup_logger()
