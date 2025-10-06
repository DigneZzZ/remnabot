"""
Mass operations handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards


@admin_only
async def mass_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show mass operations menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔄 <b>Массовые операции</b>

⚠️ Будьте осторожны! Массовые операции влияют на всех пользователей.

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.mass_operations_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_extend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mass extension"""
    query = update.callback_query
    await query.answer()
    
    text = """
📅 <b>Массовое продление подписок</b>

⚠️ Эта функция пока не реализована.

Она позволит продлить подписку всем активным пользователям сразу.
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.mass_operations_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_update_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mass update"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔄 <b>Массовое обновление</b>

⚠️ Эта функция пока не реализована.

Она позволит обновить настройки всех пользователей сразу.
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.mass_operations_menu(),
        parse_mode=ParseMode.HTML
    )


def register_mass_handlers(application):
    """Register mass operations handlers"""
    application.add_handler(CallbackQueryHandler(mass_menu_callback, pattern="^mass_menu$"))
    application.add_handler(CallbackQueryHandler(mass_extend_callback, pattern="^mass_extend$"))
    application.add_handler(CallbackQueryHandler(mass_update_callback, pattern="^mass_update$"))
    
    log.info("Mass operations handlers registered")
