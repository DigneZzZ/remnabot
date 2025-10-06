"""
Squads management handlers
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
async def squads_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show squads management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
👨‍👩‍👧‍👦 <b>Управление сквадами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.squads_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def squads_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show squads list"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка сквадов...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_squads()
        squads = response.get('data', []) if isinstance(response, dict) else response
        
        if not squads:
            text = "👨‍👩‍👧‍👦 <b>Список сквадов</b>\n\nСквады не найдены"
        else:
            text = "👨‍👩‍👧‍👦 <b>Список сквадов</b>\n\n"
            for squad in squads:
                text += formatters.format_squad(squad) + "\n\n"
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=keyboards.squads_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching squads: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка сквадов:</b>\n{str(e)}",
            reply_markup=keyboards.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squads list callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.squads_menu(),
            parse_mode=ParseMode.HTML
        )


def register_squads_handlers(application):
    """Register squads management handlers"""
    application.add_handler(CallbackQueryHandler(squads_menu_callback, pattern="^squads_menu$"))
    application.add_handler(CallbackQueryHandler(squads_list_callback, pattern="^squads_list$"))
    
    log.info("Squads handlers registered")
