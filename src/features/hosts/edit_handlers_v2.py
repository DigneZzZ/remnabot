"""
Host editing handlers - Simple approach without ConversationHandler
Uses context.user_data flags to track editing state
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client
from src.core.logger import log
from remnawave.enums import ALPN, Fingerprint, SecurityLayer


@admin_only
async def host_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start host editing - show edit menu"""
    query = update.callback_query
    await query.answer()
    
    host_uuid = query.data.split(":")[1]
    
    # Fetch host data
    try:
        response = await api_client.get_host(host_uuid)
        if not response or 'response' not in response:
            await query.edit_message_text("❌ Не удалось загрузить данные хоста")
            return
        
        host = response['response']
        
        # Store in context
        context.user_data['editing_host_uuid'] = host_uuid
        context.user_data['current_host'] = host
        
        # Show edit menu
        text = _format_edit_menu(host)
        keyboard = _build_edit_keyboard()
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error loading host for editing: {e}")
        await query.edit_message_text("❌ Ошибка при загрузке хоста")


@admin_only
async def host_field_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for editing"""
    query = update.callback_query
    await query.answer()
    
    field = query.data.split(":")[1]
    host = context.user_data.get('current_host', {})
    
    log.info(f"Field selected for editing: {field}")
    
    # For text input fields - show prompt and set waiting flag
    if field in ['remark', 'address', 'port', 'sni', 'host', 'path']:
        # Set waiting flag
        context.user_data['waiting_text_input'] = field
        context.user_data['edit_message_id'] = query.message.message_id
        context.user_data['edit_chat_id'] = query.message.chat_id
        
        # Show prompt based on field
        prompts = {
            'remark': ('Примечание', host.get('remark', 'Не указано'), 'название хоста'),
            'address': ('Адрес', host.get('address', 'Не указан'), 'IP или домен'),
            'port': ('Порт', host.get('port', 'Не указан'), 'порт (например, 443)'),
            'sni': ('SNI', host.get('sni') or 'Не указан', 'SNI'),
            'host': ('Host', host.get('host') or 'Не указан', 'Host заголовок'),
            'path': ('Path', host.get('path') or 'Не указан', 'путь'),
        }
        
        title, current, hint = prompts[field]
        text = f"""
✏️ <b>Редактирование: {title}</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новое значение ({hint}):
        """
        keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")]]
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
        log.info(f"Waiting for text input for field: {field}")
        return
    
    # For boolean/enum fields - show buttons
    if field == 'is_disabled':
        current = host.get('isDisabled', False)
        text = f"""
✏️ <b>Видимость хоста</b>

<b>Текущее значение:</b> {'🔴 Отключен' if current else '🟢 Активен'}

Выберите новое значение:
        """
        keyboard = [
            [InlineKeyboardButton("🟢 Активен", callback_data=f"host_field_set:is_disabled:false")],
            [InlineKeyboardButton("🔴 Отключен", callback_data=f"host_field_set:is_disabled:true")],
            [InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")]
        ]
    
    elif field == 'override_sni':
        current = host.get('overrideSniFromAddress', False)
        text = f"""
✏️ <b>Override SNI</b>

<b>Текущее значение:</b> {'✅ Да' if current else '❌ Нет'}

Выберите новое значение:
        """
        keyboard = [
            [InlineKeyboardButton("✅ Да", callback_data=f"host_field_set:override_sni:true")],
            [InlineKeyboardButton("❌ Нет", callback_data=f"host_field_set:override_sni:false")],
            [InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")]
        ]
    
    elif field == 'alpn':
        current = host.get('alpn')
        text = f"""
✏️ <b>ALPN</b>

<b>Текущее значение:</b> {current or 'Не указан'}

Выберите новое значение:
        """
        keyboard = []
        for alpn in ALPN:
            keyboard.append([InlineKeyboardButton(
                f"{'✓ ' if current == alpn.value else ''}{alpn.value}",
                callback_data=f"host_field_set:alpn:{alpn.value}"
            )])
        keyboard.append([InlineKeyboardButton("🗑 Очистить", callback_data=f"host_field_clear:alpn")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")])
    
    elif field == 'fingerprint':
        current = host.get('fingerprint')
        text = f"""
✏️ <b>Fingerprint</b>

<b>Текущее значение:</b> {current or 'Не указан'}

Выберите новое значение:
        """
        keyboard = []
        for fp in Fingerprint:
            keyboard.append([InlineKeyboardButton(
                f"{'✓ ' if current == fp.value else ''}{fp.value}",
                callback_data=f"host_field_set:fingerprint:{fp.value}"
            )])
        keyboard.append([InlineKeyboardButton("🗑 Очистить", callback_data=f"host_field_clear:fingerprint")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")])
    
    elif field == 'security_layer':
        current = host.get('securityLayer')
        if hasattr(current, 'value'):
            current = current.value
        text = f"""
✏️ <b>Security Layer</b>

<b>Текущее значение:</b> {current or 'Не указан'}

Выберите новое значение:
        """
        keyboard = []
        for sl in SecurityLayer:
            keyboard.append([InlineKeyboardButton(
                f"{'✓ ' if current == sl.value else ''}{sl.value}",
                callback_data=f"host_field_set:security_layer:{sl.value}"
            )])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="host_edit_cancel")])
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def host_text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global handler for text input when editing host fields"""
    # Check if we're waiting for text input
    field = context.user_data.get('waiting_text_input')
    if not field:
        return  # Not waiting for input, ignore
    
    log.info(f"✅ Text input handler triggered for field: {field}")
    log.info(f"Received text: {update.message.text}")
    
    try:
        host_uuid = context.user_data.get('editing_host_uuid')
        value = update.message.text.strip()
        
        # Delete user's message
        try:
            await update.message.delete()
        except:
            pass
        
        # Clear waiting flag
        del context.user_data['waiting_text_input']
        
        # Get message IDs for editing
        edit_message_id = context.user_data.get('edit_message_id')
        edit_chat_id = context.user_data.get('edit_chat_id')
        
        # Validate and convert value
        if field == 'port':
            try:
                value = int(value)
            except ValueError:
                await context.bot.edit_message_text(
                    "❌ Ошибка: порт должен быть числом",
                    chat_id=edit_chat_id,
                    message_id=edit_message_id
                )
                return
        
        # Update host
        await _update_host_field(context, host_uuid, field, value, edit_chat_id, edit_message_id)
        
    except Exception as e:
        log.error(f"Error in text input handler: {e}")
        edit_message_id = context.user_data.get('edit_message_id')
        edit_chat_id = context.user_data.get('edit_chat_id')
        if edit_message_id and edit_chat_id:
            await context.bot.edit_message_text(
                f"❌ Ошибка: {str(e)}",
                chat_id=edit_chat_id,
                message_id=edit_message_id
            )


@admin_only
async def host_field_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set field value from button selection"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    field = parts[1]
    value = parts[2]
    
    host_uuid = context.user_data.get('editing_host_uuid')
    
    # Convert value
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    
    await _update_host_field(context, host_uuid, field, value, query.message.chat_id, query.message.message_id)


@admin_only
async def host_field_clear_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear optional field value"""
    query = update.callback_query
    await query.answer()
    
    field = query.data.split(":")[1]
    host_uuid = context.user_data.get('editing_host_uuid')
    
    await _update_host_field(context, host_uuid, field, None, query.message.chat_id, query.message.message_id)


async def _update_host_field(context, host_uuid, field, value, chat_id, message_id):
    """Update host field via API"""
    try:
        # Map field names to API field names
        field_mapping = {
            'remark': 'remark',
            'address': 'address',
            'port': 'port',
            'is_disabled': 'isDisabled',
            'sni': 'sni',
            'host': 'host',
            'path': 'path',
            'override_sni': 'overrideSniFromAddress',
            'alpn': 'alpn',
            'fingerprint': 'fingerprint',
            'security_layer': 'securityLayer',
        }
        
        api_field = field_mapping.get(field, field)
        
        # Get current host data
        host = context.user_data.get('current_host', {})
        
        # Prepare update data
        update_data = {api_field: value}
        
        log.info(f"Updating host {host_uuid}, field {api_field} = {value}")
        
        # Update via API
        response = await api_client.update_host(host_uuid, update_data)
        
        if not response or 'response' not in response:
            await context.bot.edit_message_text(
                "❌ Ошибка при обновлении хоста",
                chat_id=chat_id,
                message_id=message_id
            )
            return
        
        # Fetch updated host
        response = await api_client.get_host(host_uuid)
        if response and 'response' in response:
            host = response['response']
            context.user_data['current_host'] = host
        
        # Show updated menu
        text = f"✅ Поле обновлено!\n\n{_format_edit_menu(host)}"
        keyboard = _build_edit_keyboard()
        
        await context.bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error updating host field: {e}")
        await context.bot.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            chat_id=chat_id,
            message_id=message_id
        )


@admin_only
async def host_edit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel host editing"""
    query = update.callback_query
    await query.answer("Отменено")
    
    # Clear editing data
    context.user_data.pop('editing_host_uuid', None)
    context.user_data.pop('current_host', None)
    context.user_data.pop('waiting_text_input', None)
    context.user_data.pop('edit_message_id', None)
    context.user_data.pop('edit_chat_id', None)
    
    await query.edit_message_text("❌ Редактирование отменено")


def _format_edit_menu(host):
    """Format host edit menu with all fields"""
    return f"""
🔧 <b>Редактирование хоста</b>

📋 <b>Основные параметры:</b>
• Примечание: <code>{host.get('remark', 'Не указано')}</code>
• Адрес: <code>{host.get('address', 'Не указан')}</code>
• Порт: <code>{host.get('port', 'Не указан')}</code>
• Видимость: {'🔴 Отключен' if host.get('isDisabled') else '🟢 Активен'}

🔐 <b>Дополнительные параметры:</b>
• SNI: <code>{host.get('sni') or 'Не указан'}</code>
• Host: <code>{host.get('host') or 'Не указан'}</code>
• Path: <code>{host.get('path') or 'Не указан'}</code>
• Override SNI: {'✅' if host.get('overrideSniFromAddress') else '❌'}
• ALPN: <code>{host.get('alpn') or 'Не указан'}</code>
• Fingerprint: <code>{host.get('fingerprint') or 'Не указан'}</code>
• Security Layer: <code>{host.get('securityLayer').value if hasattr(host.get('securityLayer'), 'value') else host.get('securityLayer') or 'Не указан'}</code>
    """.strip()


def _build_edit_keyboard():
    """Build keyboard for host editing"""
    return [
        [InlineKeyboardButton("📝 Примечание", callback_data="host_edit_field:remark")],
        [InlineKeyboardButton("🌐 Адрес", callback_data="host_edit_field:address")],
        [InlineKeyboardButton("🔌 Порт", callback_data="host_edit_field:port")],
        [InlineKeyboardButton("👁 Видимость", callback_data="host_edit_field:is_disabled")],
        [InlineKeyboardButton("➖➖➖➖➖", callback_data="host_edit_noop")],
        [InlineKeyboardButton("🔐 SNI", callback_data="host_edit_field:sni")],
        [InlineKeyboardButton("📡 Host", callback_data="host_edit_field:host")],
        [InlineKeyboardButton("📂 Path", callback_data="host_edit_field:path")],
        [InlineKeyboardButton("🔄 Override SNI", callback_data="host_edit_field:override_sni")],
        [InlineKeyboardButton("🔤 ALPN", callback_data="host_edit_field:alpn")],
        [InlineKeyboardButton("🔏 Fingerprint", callback_data="host_edit_field:fingerprint")],
        [InlineKeyboardButton("🛡 Security Layer", callback_data="host_edit_field:security_layer")],
        [InlineKeyboardButton("✅ Готово", callback_data="host_edit_done")],
    ]


@admin_only
async def host_edit_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finish editing and return to host view"""
    query = update.callback_query
    await query.answer("Сохранено")
    
    host_uuid = context.user_data.get('editing_host_uuid')
    
    # Clear editing data
    context.user_data.pop('editing_host_uuid', None)
    context.user_data.pop('current_host', None)
    context.user_data.pop('waiting_text_input', None)
    
    if not host_uuid:
        await query.edit_message_text("✅ Редактирование завершено")
        return
    
    # Import here to avoid circular dependency
    from .formatters import format_host_full
    from .keyboards import host_actions
    
    # Fetch fresh host data
    response = await api_client.get_host(host_uuid)
    if response and 'response' in response:
        host = response['response']
        text = format_host_full(host)
        keyboard = host_actions(host_uuid)
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    else:
        await query.edit_message_text("✅ Редактирование завершено")


@admin_only
async def host_edit_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop button (separator)"""
    query = update.callback_query
    await query.answer()
