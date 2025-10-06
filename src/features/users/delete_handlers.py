"""
Handlers for user deletion with smart confirmation
"""
import random
import string
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from src.features.users import keyboards as user_kb


log = logging.getLogger(__name__)


def _generate_confirmation_code(length: int = 6) -> str:
    """Generate random confirmation code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@admin_only
async def user_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user deletion with confirmation code"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        
        # Get user info
        response = await api_client.get_user(user_uuid)
        user = response.get('response', {})
        
        if not user:
            await query.edit_message_text(
                "❌ <b>Пользователь не найден</b>",
                reply_markup=user_kb.users_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Generate confirmation code
        confirmation_code = _generate_confirmation_code()
        
        # Store info in context
        context.user_data['delete_user_confirmation'] = {
            'uuid': user_uuid,
            'code': confirmation_code,
            'username': user.get('username', 'N/A')
        }
        
        username = user.get('username', 'N/A')
        tag = user.get('tag', 'N/A')
        subscription_url = user.get('subscriptionUrl', 'N/A')
        is_disabled = user.get('isDisabled', False)
        status_emoji = '🔴' if is_disabled else '🟢'
        
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"user_delete_cancel:{user_uuid}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
⚠️ <b>ВНИМАНИЕ!</b>

Вы уверены, что хотите удалить пользователя?

{status_emoji} <b>Имя:</b> {username}
🏷 <b>Тег:</b> {tag}
🔗 <b>Подписка:</b> <code>{subscription_url}</code>

❗️ <b>Это действие необратимо!</b>
Все данные пользователя и его устройства будут удалены.

Для подтверждения введите код:
<code>{confirmation_code}</code>
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error getting user for deletion: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка получения пользователя:</b>\n{str(e)}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in user delete start")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_delete_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation code input for user deletion"""
    if not update.message or not update.message.text:
        return
    
    user_code = update.message.text.strip()
    
    # Check if user is in delete confirmation flow
    delete_info = context.user_data.get('delete_user_confirmation')
    if not delete_info:
        return
    
    expected_code = delete_info.get('code')
    user_uuid = delete_info.get('uuid')
    username = delete_info.get('username')
    
    if user_code == expected_code:
        try:
            # Delete user
            await api_client.delete_user(user_uuid)
            
            # Clear state
            del context.user_data['delete_user_confirmation']
            
            keyboard = [[InlineKeyboardButton("◀️ К списку пользователей", callback_data="user_list")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ <b>Пользователь успешно удален</b>\n\n"
                f"<b>Имя:</b> {username}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except RemnaWaveAPIError as e:
            log.error(f"Error deleting user: {e}")
            # Clear state on error too
            if 'delete_user_confirmation' in context.user_data:
                del context.user_data['delete_user_confirmation']
            
            await update.message.reply_text(
                f"❌ <b>Ошибка при удалении пользователя:</b>\n{str(e)}",
                reply_markup=user_kb.users_menu(),
                parse_mode=ParseMode.HTML
            )
    else:
        # Wrong code
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"user_delete_cancel:{user_uuid}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"❌ <b>Неверный код!</b>\n\n"
            f"Ожидается: <code>{expected_code}</code>\n"
            f"Введено: <code>{user_code}</code>\n\n"
            f"Попробуйте еще раз.",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_delete_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel user deletion"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        
        # Clear state
        if 'delete_user_confirmation' in context.user_data:
            del context.user_data['delete_user_confirmation']
        
        # Get user info
        response = await api_client.get_user(user_uuid)
        user = response.get('response', {})
        
        if not user:
            await query.edit_message_text(
                "❌ <b>Пользователь не найден</b>",
                reply_markup=user_kb.users_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Show user details - redirect to user view
        from .handlers import _format_user_info
        
        text = _format_user_info(user)
        reply_markup = user_kb.user_actions(user_uuid)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in delete cancel: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in delete cancel")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
