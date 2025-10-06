"""
Authentication middleware for admin check
"""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from src.core.config import settings
from src.core.logger import log


def admin_only(func):
    """
    Decorator to restrict access to admin users only
    
    Usage:
        @admin_only
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        if not user:
            log.warning("Update without effective user")
            return
        
        if user.id not in settings.admin_id_list:
            log.warning(
                f"Unauthorized access attempt by user {user.id} "
                f"(@{user.username or 'no_username'})"
            )
            
            if update.message:
                await update.message.reply_text(
                    "⛔ У вас нет доступа к этому боту.\n"
                    "Доступ разрешен только администраторам."
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "⛔ У вас нет доступа к этому боту",
                    show_alert=True
                )
            
            return
        
        log.debug(
            f"Admin access granted to user {user.id} "
            f"(@{user.username or 'no_username'})"
        )
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


async def check_admin(user_id: int) -> bool:
    """
    Check if user is admin
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin, False otherwise
    """
    return user_id in settings.admin_id_list
