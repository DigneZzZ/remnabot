"""
HWID management handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards
from src.utils.formatters import formatters
from src.services.api import api_client, RemnaWaveAPIError


@admin_only
async def hwid_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show HWID management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
📱 <b>Управление HWID устройствами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.hwid_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def hwid_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show HWID statistics"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка статистики устройств...",
            parse_mode=ParseMode.HTML
        )
        
        stats = await api_client.get_all_devices_stats()
        
        text = formatters.format_devices_stats(stats)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching device stats: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении статистики:</b>\n{str(e)}",
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in hwid stats callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def hwid_top_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top users by device count"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка топа пользователей...",
            parse_mode=ParseMode.HTML
        )
        
        # This would need a specific API endpoint
        # For now, we'll show a placeholder
        stats = await api_client.get_all_devices_stats()
        top_users = stats.get('topUsers', [])
        
        text = formatters.format_top_users_by_devices(top_users)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching top users: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении данных:</b>\n{str(e)}",
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in hwid top users callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.hwid_menu(),
            parse_mode=ParseMode.HTML
        )


def register_hwid_handlers(application):
    """Register HWID management handlers"""
    application.add_handler(CallbackQueryHandler(hwid_menu_callback, pattern="^hwid_menu$"))
    application.add_handler(CallbackQueryHandler(hwid_stats_callback, pattern="^hwid_stats$"))
    application.add_handler(CallbackQueryHandler(hwid_top_users_callback, pattern="^hwid_top_users$"))
    
    log.info("HWID handlers registered")
