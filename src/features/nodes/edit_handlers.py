"""
Node editing handlers with simple flag-based approach
"""
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from remnawave.models.nodes import UpdateNodeRequestDto

from .formatters import format_node_full
from .keyboards import node_actions


@admin_only
async def node_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing node"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        # Fetch node details
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        if not node:
            await query.edit_message_text(
                "❌ Нода не найдена",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Store node data in context
        context.user_data['editing_node_uuid'] = node_uuid
        context.user_data['current_node'] = node
        
        # Show edit menu
        keyboard = [
            [InlineKeyboardButton("📝 Название", callback_data=f"node_edit_field:name:{node_uuid}")],
            [InlineKeyboardButton("🌐 Адрес", callback_data=f"node_edit_field:address:{node_uuid}")],
            [InlineKeyboardButton("🔌 Порт", callback_data=f"node_edit_field:port:{node_uuid}")],
            [InlineKeyboardButton("🌍 Код страны", callback_data=f"node_edit_field:country_code:{node_uuid}")],
            [InlineKeyboardButton("📊 Лимит трафика (байты)", callback_data=f"node_edit_field:traffic_limit_bytes:{node_uuid}")],
            [InlineKeyboardButton("🔔 Уведомление (%)", callback_data=f"node_edit_field:notify_percent:{node_uuid}")],
            [InlineKeyboardButton("📅 День сброса трафика", callback_data=f"node_edit_field:traffic_reset_day:{node_uuid}")],
            [InlineKeyboardButton("✅ Готово", callback_data="node_edit_done")],
            [InlineKeyboardButton("◀️ Назад", callback_data=f"node_view:{node_uuid}")]
        ]
        
        text = f"""
✏️ <b>Редактирование ноды</b>

{format_node_full(node)}

Выберите поле для редактирования:
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error starting node edit: {e}")
        await query.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_field_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for editing"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split(":")
        field = parts[1]
        node_uuid = parts[2]
        
        # Store editing context
        context.user_data['waiting_text_input'] = {
            'type': 'node_edit',
            'field': field,
            'node_uuid': node_uuid
        }
        
        # Field names mapping
        field_names = {
            'name': 'название',
            'address': 'адрес',
            'port': 'порт',
            'country_code': 'код страны (ISO 3166-1 alpha-2, например RU)',
            'traffic_limit_bytes': 'лимит трафика в байтах',
            'notify_percent': 'процент для уведомления (0-100)',
            'traffic_reset_day': 'день сброса трафика (1-31)'
        }
        
        field_name = field_names.get(field, field)
        
        await query.edit_message_text(
            f"✏️ Введите новое значение для <b>{field_name}</b>:",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error in node field select: {e}")
        await query.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for node editing"""
    if not context.user_data.get('waiting_text_input'):
        return
    
    waiting_data = context.user_data['waiting_text_input']
    
    if waiting_data.get('type') != 'node_edit':
        return
    
    try:
        user_input = update.message.text
        field = waiting_data['field']
        node_uuid = waiting_data['node_uuid']
        
        # Delete user's message
        await update.message.delete()
        
        # Fetch current node data
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        if not node:
            await update.message.reply_text("❌ Нода не найдена")
            context.user_data.pop('waiting_text_input', None)
            return
        
        # Validate and convert input based on field type
        try:
            if field == 'port':
                value = int(user_input)
                if not (1 <= value <= 65535):
                    raise ValueError("Порт должен быть от 1 до 65535")
            elif field == 'traffic_limit_bytes':
                value = int(user_input)
                if value < 0:
                    raise ValueError("Лимит не может быть отрицательным")
            elif field == 'notify_percent':
                value = int(user_input)
                if not (0 <= value <= 100):
                    raise ValueError("Процент должен быть от 0 до 100")
            elif field == 'traffic_reset_day':
                value = int(user_input)
                if not (1 <= value <= 31):
                    raise ValueError("День должен быть от 1 до 31")
            else:
                value = user_input.strip()
        except ValueError as e:
            sent_msg = await update.message.reply_text(f"❌ Неверное значение: {str(e)}")
            await sent_msg.delete()
            return
        
        # Update node via API
        await _update_node_field(update, context, node_uuid, field, value, node)
        
    except Exception as e:
        log.error(f"Error in node text input handler: {e}")
        sent_msg = await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        await sent_msg.delete()


async def _update_node_field(update, context, node_uuid, field, value, node):
    """Update single node field"""
    try:
        # Prepare update DTO with current values
        update_data = UpdateNodeRequestDto(
            uuid=node_uuid,
            name=node.get('name'),
            address=node.get('address'),
            port=node.get('port'),
            is_traffic_tracking_active=node.get('isTrafficTrackingActive', True),
            traffic_limit_bytes=node.get('trafficLimitBytes'),
            notify_percent=node.get('notifyPercent'),
            traffic_reset_day=node.get('trafficResetDay'),
            excluded_inbounds=node.get('excludedInbounds', []),
            country_code=node.get('countryCode'),
            consumption_multiplier=node.get('consumptionMultiplier', 1.0)
        )
        
        # Update the specific field
        setattr(update_data, field, value)
        
        # Update via API
        await api_client.update_node(update_data)
        
        # Clear waiting state
        context.user_data.pop('waiting_text_input', None)
        
        # Show success and return to edit menu
        sent_msg = await update.message.reply_text(
            "✅ Поле успешно обновлено!",
            parse_mode=ParseMode.HTML
        )
        await sent_msg.delete()
        
        # Refresh edit menu
        await _show_edit_menu(update, context, node_uuid)
        
    except RemnaWaveAPIError as e:
        log.error(f"Error updating node: {e}")
        sent_msg = await update.message.reply_text(f"❌ Ошибка при обновлении: {str(e)}")
        await sent_msg.delete()
        context.user_data.pop('waiting_text_input', None)


async def _show_edit_menu(update, context, node_uuid):
    """Show edit menu after update"""
    try:
        # Fetch fresh node data
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        keyboard = [
            [InlineKeyboardButton("📝 Название", callback_data=f"node_edit_field:name:{node_uuid}")],
            [InlineKeyboardButton("🌐 Адрес", callback_data=f"node_edit_field:address:{node_uuid}")],
            [InlineKeyboardButton("🔌 Порт", callback_data=f"node_edit_field:port:{node_uuid}")],
            [InlineKeyboardButton("🌍 Код страны", callback_data=f"node_edit_field:country_code:{node_uuid}")],
            [InlineKeyboardButton("📊 Лимит трафика (байты)", callback_data=f"node_edit_field:traffic_limit_bytes:{node_uuid}")],
            [InlineKeyboardButton("🔔 Уведомление (%)", callback_data=f"node_edit_field:notify_percent:{node_uuid}")],
            [InlineKeyboardButton("📅 День сброса трафика", callback_data=f"node_edit_field:traffic_reset_day:{node_uuid}")],
            [InlineKeyboardButton("✅ Готово", callback_data="node_edit_done")],
            [InlineKeyboardButton("◀️ Назад", callback_data=f"node_view:{node_uuid}")]
        ]
        
        text = f"""
✏️ <b>Редактирование ноды</b>

{format_node_full(node)}

Выберите поле для редактирования:
        """
        
        # Store message ID for editing
        if 'editing_message_id' in context.user_data:
            await context.bot.edit_message_text(
                text=text.strip(),
                chat_id=update.effective_chat.id,
                message_id=context.user_data['editing_message_id'],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        else:
            sent_msg = await update.message.reply_text(
                text.strip(),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            context.user_data['editing_message_id'] = sent_msg.message_id
            
    except Exception as e:
        log.error(f"Error showing edit menu: {e}")


@admin_only
async def node_edit_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finish editing and return to node view"""
    query = update.callback_query
    await query.answer("Сохранено")
    
    node_uuid = context.user_data.get('editing_node_uuid')
    
    # Clear editing data
    context.user_data.pop('editing_node_uuid', None)
    context.user_data.pop('current_node', None)
    context.user_data.pop('waiting_text_input', None)
    context.user_data.pop('editing_message_id', None)
    
    if not node_uuid:
        await query.edit_message_text("✅ Редактирование завершено")
        return
    
    # Fetch fresh node data
    response = await api_client.get_node(node_uuid)
    if response and 'response' in response:
        node = response['response']
        text = format_node_full(node)
        keyboard = node_actions(node_uuid)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await query.edit_message_text("✅ Редактирование завершено")
