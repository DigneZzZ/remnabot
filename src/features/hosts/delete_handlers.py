"""
Handlers for host deletion with smart confirmation
"""
import random
import string
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from src.features.hosts import keyboards as host_kb


log = logging.getLogger(__name__)


def _generate_confirmation_code(length: int = 6) -> str:
    """Generate random confirmation code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@admin_only
async def host_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start host deletion with confirmation code"""
    query = update.callback_query
    await query.answer()
    
    try:
        host_uuid = query.data.split(":")[1]
        
        # Get host info
        response = await api_client.get_host(host_uuid)
        host = response.get('response', {})
        
        if not host:
            await query.edit_message_text(
                "❌ <b>Хост не найден</b>",
                reply_markup=host_kb.hosts_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Generate confirmation code
        confirmation_code = _generate_confirmation_code()
        
        # Store info in context
        context.user_data['delete_host_confirmation'] = {
            'uuid': host_uuid,
            'code': confirmation_code,
            'name': host.get('remark', 'N/A')
        }
        
        host_name = host.get('remark', 'N/A')
        address = host.get('address', 'N/A')
        port = host.get('port', 'N/A')
        inbound_tag = host.get('inboundTag', 'N/A')
        
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_delete_cancel:{host_uuid}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
⚠️ <b>ВНИМАНИЕ!</b>

Вы уверены, что хотите удалить хост?

<b>Название:</b> {host_name}
<b>Адрес:</b> <code>{address}:{port}</code>
<b>Inbound:</b> {inbound_tag}

❗️ <b>Это действие необратимо!</b>

Для подтверждения введите код:
<code>{confirmation_code}</code>
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error getting host for deletion: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка получения хоста:</b>\n{str(e)}",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in host delete start")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def host_delete_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation code input for host deletion"""
    if not update.message or not update.message.text:
        return
    
    user_code = update.message.text.strip()
    
    # Check if user is in delete confirmation flow
    delete_info = context.user_data.get('delete_host_confirmation')
    if not delete_info:
        return
    
    expected_code = delete_info.get('code')
    host_uuid = delete_info.get('uuid')
    host_name = delete_info.get('name')
    
    if user_code == expected_code:
        try:
            # Delete host
            await api_client.delete_host(host_uuid)
            
            # Clear state
            del context.user_data['delete_host_confirmation']
            
            keyboard = [[InlineKeyboardButton("◀️ К списку хостов", callback_data="hosts_list")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ <b>Хост успешно удален</b>\n\n"
                f"<b>Название:</b> {host_name}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except RemnaWaveAPIError as e:
            log.error(f"Error deleting host: {e}")
            # Clear state on error too
            if 'delete_host_confirmation' in context.user_data:
                del context.user_data['delete_host_confirmation']
            
            await update.message.reply_text(
                f"❌ <b>Ошибка при удалении хоста:</b>\n{str(e)}",
                reply_markup=host_kb.hosts_menu(),
                parse_mode=ParseMode.HTML
            )
    else:
        # Wrong code
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_delete_cancel:{host_uuid}")]
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
async def host_delete_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel host deletion"""
    query = update.callback_query
    await query.answer()
    
    try:
        host_uuid = query.data.split(":")[1]
        
        # Clear state
        if 'delete_host_confirmation' in context.user_data:
            del context.user_data['delete_host_confirmation']
        
        # Get host info
        response = await api_client.get_host(host_uuid)
        host = response.get('response', {})
        
        if not host:
            await query.edit_message_text(
                "❌ <b>Хост не найден</b>",
                reply_markup=host_kb.hosts_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Show host details
        host_name = host.get('remark', 'N/A')
        address = host.get('address', 'N/A')
        port = host.get('port', 'N/A')
        inbound_tag = host.get('inboundTag', 'N/A')
        
        text = f"""
🖥 <b>Хост: {host_name}</b>

<b>Адрес:</b> <code>{address}:{port}</code>
<b>Inbound:</b> {inbound_tag}
        """
        
        reply_markup = host_kb.host_actions(host_uuid)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in delete cancel: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in delete cancel")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
