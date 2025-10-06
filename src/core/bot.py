"""
Bot initialization module
"""
from telegram.ext import Application
from src.core.config import settings
from src.core.logger import log


def create_bot_application() -> Application:
    """
    Create and configure Telegram bot application
    
    Returns:
        Application: Configured bot application
    """
    log.info("Creating bot application...")
    
    # Create application
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .concurrent_updates(True)
        .build()
    )
    
    log.info("Bot application created successfully")
    return application
