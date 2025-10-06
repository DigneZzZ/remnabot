"""
Mass operations handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as mass_kb
from . import formatters as mass_fmt


@admin_only
async def mass_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show mass operations menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔄 <b>Массовые операции</b>

⚠️ <b>Внимание!</b> Операции применяются ко всем пользователям.

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=mass_kb.mass_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_extend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show extend days selection"""
    query = update.callback_query
    await query.answer()
    
    text = """
⏰ <b>Продлить всем пользователям</b>

Выберите количество дней для продления:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=mass_kb.extend_days_keyboard(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_extend_days_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process mass extend with selected days"""
    query = update.callback_query
    await query.answer()
    
    try:
        days = int(query.data.split(":")[1])
        
        # Store days in context for confirmation
        context.user_data['mass_extend_days'] = days
        
        text = f"""
⏰ <b>Подтверждение операции</b>

Вы действительно хотите продлить <b>всем</b> пользователям на <b>{days} дней</b>?

⚠️ Это действие нельзя отменить!
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=mass_kb.confirmation_keyboard(f"extend:{days}"),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.exception("Error in mass extend days")
        await query.edit_message_text(
            "❌ <b>Ошибка</b>",
            reply_markup=mass_kb.mass_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def mass_activate_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm mass activation"""
    query = update.callback_query
    await query.answer()
    
    text = """
✅ <b>Подтверждение активации</b>

Вы действительно хотите <b>активировать всех</b> пользователей?

⚠️ Это действие нельзя отменить!
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=mass_kb.confirmation_keyboard("activate"),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_deactivate_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm mass deactivation"""
    query = update.callback_query
    await query.answer()
    
    text = """
⏸️ <b>Подтверждение деактивации</b>

Вы действительно хотите <b>деактивировать всех</b> пользователей?

⚠️ Это действие нельзя отменить!
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=mass_kb.confirmation_keyboard("deactivate"),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_reset_traffic_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm mass traffic reset"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔄 <b>Подтверждение сброса трафика</b>

Вы действительно хотите <b>сбросить трафик всем</b> пользователям?

⚠️ Это действие нельзя отменить!
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=mass_kb.confirmation_keyboard("reset_traffic"),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def mass_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute confirmed mass operation"""
    query = update.callback_query
    await query.answer()
    
    try:
        operation = query.data.split(":", 1)[1]
        
        await query.edit_message_text(
            "⏳ Выполняется массовая операция...\nЭто может занять некоторое время.",
            parse_mode=ParseMode.HTML
        )
        
        if operation.startswith("extend:"):
            days = int(operation.split(":")[1])
            response = await api_client.mass_extend_users(days)
        elif operation == "activate":
            response = await api_client.mass_activate_users()
        elif operation == "deactivate":
            response = await api_client.mass_deactivate_users()
        elif operation == "reset_traffic":
            response = await api_client.mass_reset_traffic()
        else:
            await query.edit_message_text(
                "❌ Неизвестная операция",
                reply_markup=mass_kb.mass_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        result = response.get('response', {})
        text = mass_fmt.format_operation_result(result)
        
        await query.edit_message_text(
            text,
            reply_markup=mass_kb.mass_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in mass operation: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=mass_kb.mass_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in mass operation")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=mass_kb.mass_menu(),
            parse_mode=ParseMode.HTML
        )


def register_mass_handlers(application):
    """Register all mass operations handlers"""
    application.add_handler(CallbackQueryHandler(mass_menu_callback, pattern="^mass_menu$"))
    application.add_handler(CallbackQueryHandler(mass_extend_callback, pattern="^mass_extend$"))
    application.add_handler(CallbackQueryHandler(mass_extend_days_callback, pattern="^mass_extend_days:"))
    application.add_handler(CallbackQueryHandler(mass_activate_confirm_callback, pattern="^mass_activate$"))
    application.add_handler(CallbackQueryHandler(mass_deactivate_confirm_callback, pattern="^mass_deactivate$"))
    application.add_handler(CallbackQueryHandler(mass_reset_traffic_confirm_callback, pattern="^mass_reset_traffic$"))
    application.add_handler(CallbackQueryHandler(mass_confirm_callback, pattern="^mass_confirm:"))
    
    log.info("✅ Mass operations feature handlers registered")
