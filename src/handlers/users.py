"""
Users management handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode

from src.core.logger import log
from src.core.config import settings
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards
from src.utils.formatters import formatters
from src.utils.validators import validators
from src.services.api import api_client, RemnaWaveAPIError

# Conversation states
AWAITING_PIN = 1


@admin_only
async def users_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
👥 <b>Управление пользователями</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.users_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def users_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users list"""
    query = update.callback_query
    await query.answer()
    
    # Extract page from callback data
    page = 1
    if ":" in query.data:
        try:
            page = int(query.data.split(":")[1])
        except (IndexError, ValueError):
            page = 1
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка пользователей...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch users
        response = await api_client.get_users(page=page, limit=10)
        # API returns data in 'response' wrapper
        data = response.get('response', {})
        users = data.get('users', [])
        total = data.get('total', 0)
        total_pages = (total + 9) // 10  # Ceiling division
        
        if not users:
            text = "👥 <b>Список пользователей</b>\n\nПользователи не найдены"
            keyboard = [[keyboards.back_to_main().inline_keyboard[0][0]]]
        else:
            text = f"👥 <b>Список пользователей</b> (страница {page}/{total_pages})\n"
            text += f"<i>Всего: {total} пользователей</i>\n\n"
            text += "Выберите пользователя для управления:"
            
            # Build keyboard with user buttons
            keyboard = []
            for user in users:
                username = user.get('username', 'N/A')
                status = user.get('status', 'unknown').upper()
                uuid = user.get('uuid', '')
                
                # Emoji для статуса
                status_emoji = {
                    'ACTIVE': '✅',
                    'DISABLED': '🚫',
                    'LIMITED': '⚠️',
                    'EXPIRED': '⏱️'
                }.get(status, '❓')
                
                button_text = f"{status_emoji} {username}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"user_view:{uuid}")])
            
            # Add pagination if needed
            if total_pages > 1:
                keyboard.append(keyboards.pagination(page, total_pages, "users_page"))
            
            # Add back button
            keyboard.append([keyboards.back_to_main().inline_keyboard[0][0]])
        
        from telegram import InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching users: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка пользователей:</b>\n{str(e)}",
            reply_markup=keyboards.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in users list callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.users_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed user information"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации о пользователе...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch user details
        response = await api_client.get_user(user_uuid)
        user = response.get('response', {})
        
        if not user:
            await query.edit_message_text(
                "❌ Пользователь не найден",
                reply_markup=keyboards.users_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format user info
        text = formatters.format_user(user)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboards.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching user: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении пользователя:</b>\n{str(e)}",
            reply_markup=keyboards.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in user view callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.users_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_extend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription extension presets"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    text = """
📅 <b>Продление подписки</b>

Выберите период продления:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.extend_presets(user_uuid),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def extend_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extend user subscription"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split(":")
        user_uuid = parts[1]
        days = int(parts[2])
        
        await query.edit_message_text(
            f"⏳ Продление подписки на {days} дней...",
            parse_mode=ParseMode.HTML
        )
        
        result = await api_client.extend_user_subscription(user_uuid, days)
        
        await query.edit_message_text(
            f"✅ <b>Подписка успешно продлена на {days} дней</b>",
            reply_markup=keyboards.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error extending subscription: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при продлении подписки:</b>\n{str(e)}",
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in extend user callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_delete_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show delete confirmation"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    text = """
⚠️ <b>Подтверждение удаления</b>

Вы уверены, что хотите удалить этого пользователя?

Для подтверждения введите PIN-код.
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.confirm_delete(user_uuid),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def user_delete_pin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request PIN for deletion"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    context.user_data['delete_user_uuid'] = user_uuid
    context.user_data['awaiting_delete_pin'] = True
    
    text = f"""
🔐 <b>Введите PIN-код для подтверждения удаления</b>

Отправьте PIN-код в следующем сообщении.
Для отмены отправьте /cancel
    """
    
    await query.edit_message_text(
        text.strip(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def handle_delete_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PIN input for deletion"""
    if not context.user_data.get('awaiting_delete_pin'):
        return
    
    pin = update.message.text.strip()
    user_uuid = context.user_data.get('delete_user_uuid')
    
    is_valid, error = validators.validate_pin(pin, settings.pin_code)
    
    if not is_valid:
        await update.message.reply_text(
            f"❌ {error}\n\nПопробуйте снова или отправьте /cancel",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Clear state
    context.user_data.pop('awaiting_delete_pin', None)
    context.user_data.pop('delete_user_uuid', None)
    
    try:
        await update.message.reply_text(
            "⏳ Удаление пользователя...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.delete_user(user_uuid)
        
        await update.message.reply_text(
            "✅ <b>Пользователь успешно удален</b>",
            reply_markup=keyboards.users_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error deleting user: {e}")
        await update.message.reply_text(
            f"❌ <b>Ошибка при удалении пользователя:</b>\n{str(e)}",
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )


# Register handlers
def register_users_handlers(application):
    """Register users management handlers"""
    application.add_handler(CallbackQueryHandler(users_menu_callback, pattern="^users_menu$"))
    application.add_handler(CallbackQueryHandler(users_list_callback, pattern="^users_list$"))
    application.add_handler(CallbackQueryHandler(users_list_callback, pattern="^users_page:"))
    application.add_handler(CallbackQueryHandler(user_view_callback, pattern="^user_view:"))
    application.add_handler(CallbackQueryHandler(user_extend_callback, pattern="^user_extend:"))
    application.add_handler(CallbackQueryHandler(extend_user_callback, pattern="^extend:"))
    application.add_handler(CallbackQueryHandler(user_delete_confirm_callback, pattern="^user_delete_confirm:"))
    application.add_handler(CallbackQueryHandler(user_delete_pin_callback, pattern="^user_delete_pin:"))
    
    # Message handler for PIN input
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_delete_pin
    ))
    
    log.info("Users handlers registered")
