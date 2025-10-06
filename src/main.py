"""
Main entry point for Remnawave Telegram Bot
"""
import asyncio
import sys
from telegram.ext import Application

from src.core.config import settings
from src.core.logger import log
from src.core.bot import create_bot_application
from src.services.api import api_client
from src.services.cache import cache_service

# Import handlers
from src.handlers.start import register_start_handlers

# Import feature handlers
from src.features.users import register_users_handlers
from src.features.hosts import register_hosts_handlers
from src.features.nodes import register_nodes_handlers
from src.features.hwid import register_hwid_handlers
from src.features.squads import register_squads_handlers
from src.features.mass_operations import register_mass_handlers
from src.features.system import register_system_handlers


async def on_startup(application: Application):
    """Called on bot startup"""
    log.info("Bot is starting up...")
    
    # Connect to Redis if enabled
    await cache_service.connect()
    
    # Test API connection with SDK
    try:
        log.info("Testing Remnawave API connection with SDK...")
        # Try to get system stats to verify connection
        stats = await api_client.get_system_stats()
        log.info(f"✅ Successfully connected to Remnawave API")
        log.info(f"System stats: {stats}")
    except Exception as e:
        log.error(f"❌ Failed to connect to Remnawave API: {e}")
        log.error("Bot will continue but API calls may fail")
    
    log.info("Bot startup completed")


async def on_shutdown(application: Application):
    """Called on bot shutdown"""
    log.info("Bot is shutting down...")
    
    # Close API client
    await api_client.close()
    
    # Disconnect from Redis
    await cache_service.disconnect()
    
    log.info("Bot shutdown completed")


def main():
    """Main function"""
    log.info("=" * 60)
    log.info("Remnawave Telegram Bot")
    log.info("=" * 60)
    log.info(f"Debug mode: {settings.is_debug}")
    log.info(f"Log level: {settings.log_level}")
    log.info(f"Admins: {len(settings.admin_id_list)} user(s)")
    log.info(f"API URL: {settings.remnawave_api_url}")
    log.info(f"Redis enabled: {settings.redis_enabled}")
    log.info("=" * 60)
    
    # Validate configuration
    if not settings.telegram_bot_token:
        log.error("TELEGRAM_BOT_TOKEN is not set!")
        sys.exit(1)
    
    if not settings.admin_id_list:
        log.error("ADMIN_IDS is not set or invalid!")
        sys.exit(1)
    
    if not settings.remnawave_api_url:
        log.error("REMNAWAVE_API_URL is not set!")
        sys.exit(1)
    
    # Create bot application
    application = create_bot_application()
    
    # Add debug middleware to log all updates
    async def log_update(update, context):
        if update.message and update.message.text:
            log.info(f"📩 INCOMING MESSAGE: '{update.message.text}' from user {update.effective_user.id}")
        elif update.callback_query:
            log.info(f"🔘 INCOMING CALLBACK: '{update.callback_query.data}' from user {update.effective_user.id}")
    
    from telegram.ext import TypeHandler
    from telegram import Update as TelegramUpdate
    application.add_handler(TypeHandler(TelegramUpdate, log_update), group=-1)
    
    # Register handlers
    log.info("Registering handlers...")
    register_start_handlers(application)
    
    # Register feature handlers
    log.info("Registering feature modules...")
    register_users_handlers(application)
    register_hosts_handlers(application)
    register_nodes_handlers(application)
    register_hwid_handlers(application)
    register_squads_handlers(application)
    register_mass_handlers(application)
    register_system_handlers(application)
    log.info("All handlers registered")
    
    # Add startup and shutdown callbacks
    application.post_init = on_startup
    application.post_shutdown = on_shutdown
    
    # Start the bot
    log.info("Starting bot polling...")
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
    except Exception as e:
        log.exception(f"Bot crashed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
