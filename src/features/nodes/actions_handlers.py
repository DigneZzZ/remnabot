"""
Node actions handlers: stats, restart, smart delete
"""
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as node_kb


def _generate_confirmation_code(length=6):
    """Generate random confirmation code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@admin_only
async def node_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show node statistics"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка статистики...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch node details
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        if not node:
            await query.edit_message_text(
                "❌ Нода не найдена",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format statistics
        name = node.get('name', 'N/A')
        address = node.get('address', 'N/A')
        port = node.get('port', 'N/A')
        is_disabled = node.get('isDisabled', False)
        country_code = node.get('countryCode', 'N/A')
        
        # Traffic info
        traffic_limit = node.get('trafficLimitBytes', 0)
        traffic_used = node.get('trafficUsedBytes', 0)
        is_tracking = node.get('isTrafficTrackingActive', False)
        notify_percent = node.get('notifyPercent', 0)
        traffic_reset_day = node.get('trafficResetDay', 0)
        consumption_multiplier = node.get('consumptionMultiplier', 1.0)
        users_count = len(node.get('users', []))
        
        status_emoji = '🔴' if is_disabled else '🟢'
        tracking_emoji = '✅' if is_tracking else '❌'
        
        # Format traffic used
        def format_bytes(bytes_val):
            if bytes_val >= 1024**4:
                return f"{bytes_val / (1024**4):.2f} TB"
            elif bytes_val >= 1024**3:
                return f"{bytes_val / (1024**3):.2f} GB"
            elif bytes_val >= 1024**2:
                return f"{bytes_val / (1024**2):.2f} MB"
            elif bytes_val >= 1024:
                return f"{bytes_val / 1024:.2f} KB"
            else:
                return f"{bytes_val} Б"
        
        traffic_used_str = format_bytes(traffic_used)
        traffic_limit_str = format_bytes(traffic_limit) if traffic_limit else "Не установлен"
        
        # Calculate percentage if limit is set
        if traffic_limit and traffic_limit > 0:
            usage_percent = (traffic_used / traffic_limit) * 100
            usage_bar = "█" * int(usage_percent / 10) + "░" * (10 - int(usage_percent / 10))
            usage_info = f"\n📈 <b>Использовано:</b> {usage_percent:.1f}% [{usage_bar}]"
        else:
            usage_info = ""
        
        text = f"""
📊 <b>Статистика ноды</b>

{status_emoji} <b>Название:</b> {name}
🌐 <b>Адрес:</b> <code>{address}:{port}</code>
🌍 <b>Страна:</b> {country_code}
📈 <b>Множитель потребления:</b> {consumption_multiplier}x
👥 <b>Пользователей:</b> {users_count}

<b>Трафик:</b>
{tracking_emoji} <b>Отслеживание:</b> {'Включено' if is_tracking else 'Выключено'}
📊 <b>Лимит:</b> {traffic_limit_str}
📥 <b>Потреблено:</b> {traffic_used_str}{usage_info}
🔔 <b>Уведомление:</b> {notify_percent}%
📅 <b>День сброса:</b> {traffic_reset_day} число месяца
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data=f"node_stats:{node_uuid}")],
            [InlineKeyboardButton("◀️ Назад", callback_data=f"node_view:{node_uuid}")]
        ]
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching node stats: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node stats")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_restart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart single node"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Перезапуск ноды...",
            parse_mode=ParseMode.HTML
        )
        
        # Restart node via API
        await api_client.restart_node(node_uuid)
        
        await query.edit_message_text(
            "✅ <b>Нода успешно перезапущена</b>",
            reply_markup=node_kb.node_actions(node_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error restarting node: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при перезапуске:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node restart")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable/disable node"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split(":")
        action = parts[0]  # node_enable or node_disable
        node_uuid = parts[1]
        
        await query.edit_message_text(
            "⏳ Обновление статуса...",
            parse_mode=ParseMode.HTML
        )
        
        # Enable or disable via API
        if action == "node_enable":
            await api_client.enable_node(node_uuid)
            status_text = "включена"
        else:
            await api_client.disable_node(node_uuid)
            status_text = "выключена"
        
        # Fetch updated node data
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        from .formatters import format_node_full
        text = f"✅ <b>Нода {status_text}</b>\n\n{format_node_full(node)}"
        
        await query.edit_message_text(
            text,
            reply_markup=node_kb.node_actions(node_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error toggling node: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node toggle")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start smart delete process with confirmation code"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        # Fetch node info
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        if not node:
            await query.edit_message_text(
                "❌ Нода не найдена",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Generate confirmation code
        code = _generate_confirmation_code()
        
        # Store in context
        context.user_data['delete_node_confirmation'] = {
            'node_uuid': node_uuid,
            'code': code,
            'node_name': node.get('name', 'Unknown')
        }
        
        name = node.get('name', 'N/A')
        address = node.get('address', 'N/A')
        port = node.get('port', 'N/A')
        
        text = f"""
⚠️ <b>ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ НОДЫ</b>

🗑 <b>Нода:</b> {name}
🌐 <b>Адрес:</b> {address}:{port}

⚠️ <b>Внимание!</b> Это действие необратимо!

Для подтверждения удаления введите код:
<code>{code}</code>

Или нажмите "Отмена" для возврата.
        """
        
        keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data=f"node_delete_cancel:{node_uuid}")]]
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error starting node delete: {e}")
        await query.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_delete_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete confirmation code input"""
    if not context.user_data.get('delete_node_confirmation'):
        return
    
    try:
        user_input = update.message.text.strip()
        delete_data = context.user_data['delete_node_confirmation']
        
        # Delete user's message
        await update.message.delete()
        
        if user_input != delete_data['code']:
            sent_msg = await update.message.reply_text(
                "❌ Неверный код подтверждения",
                parse_mode=ParseMode.HTML
            )
            await sent_msg.delete()
            return
        
        # Code is correct, proceed with deletion
        node_uuid = delete_data['node_uuid']
        node_name = delete_data['node_name']
        
        sent_msg = await update.message.reply_text(
            "⏳ Удаление ноды...",
            parse_mode=ParseMode.HTML
        )
        
        try:
            await api_client.delete_node(node_uuid)
            
            # Clear confirmation data
            context.user_data.pop('delete_node_confirmation', None)
            
            await sent_msg.edit_text(
                f"✅ <b>Нода '{node_name}' успешно удалена</b>",
                reply_markup=node_kb.nodes_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except RemnaWaveAPIError as e:
            log.error(f"Error deleting node: {e}")
            await sent_msg.edit_text(
                f"❌ <b>Ошибка при удалении:</b>\n{str(e)}",
                reply_markup=node_kb.nodes_menu(),
                parse_mode=ParseMode.HTML
            )
            context.user_data.pop('delete_node_confirmation', None)
            
    except Exception as e:
        log.exception("Unexpected error in node delete confirm")
        sent_msg = await update.message.reply_text(
            f"❌ Ошибка: {str(e)}",
            parse_mode=ParseMode.HTML
        )
        await sent_msg.delete()
        context.user_data.pop('delete_node_confirmation', None)


@admin_only
async def node_delete_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel node deletion"""
    query = update.callback_query
    await query.answer("Отменено")
    
    node_uuid = query.data.split(":")[1]
    
    # Clear confirmation data
    context.user_data.pop('delete_node_confirmation', None)
    
    # Return to node view
    try:
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        from .formatters import format_node_full
        text = format_node_full(node)
        
        await query.edit_message_text(
            text,
            reply_markup=node_kb.node_actions(node_uuid),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.error(f"Error in delete cancel: {e}")
        await query.edit_message_text(
            "❌ Удаление отменено",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
