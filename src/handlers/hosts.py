"""
Hosts management handlers
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
async def hosts_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hosts management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🖥️ <b>Управление хостами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.hosts_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def hosts_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hosts list"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка хостов...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_hosts()
        # API returns data in 'response' wrapper
        hosts = response.get('response', []) if isinstance(response, dict) else response
        
        if not hosts:
            text = "🖥️ <b>Список хостов</b>\n\nХосты не найдены"
        else:
            text = "🖥️ <b>Список хостов</b>\n\n"
            for host in hosts:
                text += formatters.format_host(host) + "\n\n"
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=keyboards.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching hosts: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка хостов:</b>\n{str(e)}",
            reply_markup=keyboards.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in hosts list callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.hosts_menu(),
            parse_mode=ParseMode.HTML
        )


def register_hosts_handlers(application):
    """Register hosts management handlers"""
    application.add_handler(CallbackQueryHandler(hosts_menu_callback, pattern="^hosts_menu$"))
    application.add_handler(CallbackQueryHandler(hosts_list_callback, pattern="^hosts_list$"))
    
    log.info("Hosts handlers registered")
