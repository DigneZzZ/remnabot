"""
System management handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as sys_kb
from . import formatters as sys_fmt


@admin_only
async def system_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
⚙️ <b>Системные настройки</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=sys_kb.system_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def system_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system statistics"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка статистики...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_system_stats()
        stats = response.get('response', {})
        
        text = sys_fmt.format_system_stats(stats)
        
        await query.edit_message_text(
            text,
            reply_markup=sys_kb.system_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching system stats: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении статистики:</b>\n{str(e)}",
            reply_markup=sys_kb.system_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in system stats")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=sys_kb.system_menu(),
            parse_mode=ParseMode.HTML
        )


def register_system_handlers(application):
    """Register all system management handlers"""
    application.add_handler(CallbackQueryHandler(system_menu_callback, pattern="^system_menu$"))
    application.add_handler(CallbackQueryHandler(system_stats_callback, pattern="^system_stats$"))
    
    log.info("✅ System feature handlers registered")
