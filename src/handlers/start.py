"""
Start command and main menu handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards
from src.utils.formatters import formatters
from src.services.api import api_client, RemnaWaveAPIError


@admin_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    log.info(f"User {user.id} (@{user.username}) started the bot")
    
    welcome_text = f"""
👋 <b>Добро пожаловать, {user.first_name}!</b>

Это бот управления Remnawave панелью.

Выберите действие из меню ниже:
    """
    
    await update.message.reply_text(
        welcome_text.strip(),
        reply_markup=keyboards.main_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu callback"""
    query = update.callback_query
    await query.answer()
    
    welcome_text = """
🏠 <b>Главное меню</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        welcome_text.strip(),
        reply_markup=keyboards.main_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle statistics callback"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Show loading message
        await query.edit_message_text(
            "⏳ Загрузка статистики...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch statistics
        stats = await api_client.get_system_stats()
        
        stats_text = formatters.format_system_stats(stats)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching statistics: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении статистики:</b>\n{str(e)}",
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in stats callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def refresh_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle refresh main menu callback"""
    query = update.callback_query
    await query.answer("🔄 Обновлено")
    
    await main_menu_callback(update, context)


@admin_only
async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle no-operation callback (for non-clickable buttons)"""
    query = update.callback_query
    await query.answer()


# Register handlers
def register_start_handlers(application):
    """Register start and main menu handlers"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats$"))
    application.add_handler(CallbackQueryHandler(refresh_main_callback, pattern="^refresh_main$"))
    application.add_handler(CallbackQueryHandler(noop_callback, pattern="^noop$"))
    
    log.info("Start handlers registered")
