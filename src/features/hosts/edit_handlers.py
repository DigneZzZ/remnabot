"""
Host edit handlers with ConversationHandler
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from remnawave.enums.alpn import ALPN
from remnawave.enums.fingerprint import Fingerprint
from remnawave.enums.security_layer import SecurityLayer

# States
SELECTING_FIELD, EDITING_FIELD = range(2)


@admin_only
async def host_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start host editing - show current settings and field selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        host_uuid = query.data.split(":")[1]
        context.user_data['editing_host_uuid'] = host_uuid
        
        await query.edit_message_text(
            "⏳ Загрузка настроек хоста...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch host details
        response = await api_client.get_host(host_uuid)
        host = response.get('response', {})
        
        if not host:
            await query.edit_message_text(
                "❌ Хост не найден",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        # Store host data
        context.user_data['current_host'] = host
        
        # Show current settings with edit buttons
        text = _format_edit_menu(host)
        keyboard = _build_edit_keyboard(host_uuid)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return SELECTING_FIELD
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching host for edit: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error in host edit start")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def host_field_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for editing"""
    query = update.callback_query
    await query.answer()
    
    field = query.data.split(":")[1]
    context.user_data['editing_field'] = field
    host = context.user_data.get('current_host', {})
    
    # Show current value and editing options
    if field == 'remark':
        current = host.get('remark') or 'Не указано'
        text = f"""
✏️ <b>Редактирование примечания</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новое примечание (название хоста):
        """
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'address':
        current = host.get('address') or 'Не указан'
        text = f"""
✏️ <b>Редактирование адреса</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новый адрес (IP или домен):
        """
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'port':
        current = host.get('port') or 'Не указан'
        text = f"""
✏️ <b>Редактирование порта</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новый порт (например, 443):
        """
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'is_disabled':
        current = host.get('isDisabled', False)
        text = f"""
✏️ <b>Видимость хоста</b>

<b>Текущее значение:</b> {'🔴 Отключен' if current else '🟢 Активен'}

Выберите новое значение:
        """
        keyboard = [
            [InlineKeyboardButton("🟢 Активен", callback_data=f"host_field_set:is_disabled:false")],
            [InlineKeyboardButton("🔴 Отключен", callback_data=f"host_field_set:is_disabled:true")],
            [InlineKeyboardButton("◀️ Назад", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'sni':
        current = host.get('sni') or 'Не указан'
        text = f"""
✏️ <b>Редактирование SNI</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новое значение SNI или используйте кнопку ниже:
        """
        keyboard = [
            [InlineKeyboardButton("🗑️ Очистить (не использовать)", callback_data=f"host_field_clear:sni")],
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'host':
        current = host.get('host') or 'Не указан'
        text = f"""
✏️ <b>Редактирование Host</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новое значение Host:
        """
        keyboard = [
            [InlineKeyboardButton("🗑️ Очистить", callback_data=f"host_field_clear:host")],
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'path':
        current = host.get('path') or 'Не указан'
        text = f"""
✏️ <b>Редактирование Path</b>

<b>Текущее значение:</b> <code>{current}</code>

Введите новый путь (например, /api/v1):
        """
        keyboard = [
            [InlineKeyboardButton("🗑️ Очистить", callback_data=f"host_field_clear:path")],
            [InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'override_sni':
        current = host.get('overrideSniFromAddress', False)
        text = f"""
✏️ <b>Переопределить SNI из адреса</b>

<b>Текущее значение:</b> {'✅ Включено' if current else '❌ Выключено'}

Выберите новое значение:
        """
        keyboard = [
            [InlineKeyboardButton("✅ Включить", callback_data=f"host_field_set:override_sni:true")],
            [InlineKeyboardButton("❌ Выключить", callback_data=f"host_field_set:override_sni:false")],
            [InlineKeyboardButton("◀️ Назад", callback_data=f"host_edit_cancel")]
        ]
        
    elif field == 'alpn':
        current = host.get('alpn') or 'Не указан'
        text = f"""
✏️ <b>Редактирование ALPN</b>

<b>Текущее значение:</b> <code>{current}</code>

Выберите новое значение:
        """
        alpn_values = [e.value for e in ALPN]
        keyboard = []
        for alpn in alpn_values:
            emoji = "✅" if alpn == current else "◽"
            keyboard.append([InlineKeyboardButton(f"{emoji} {alpn}", callback_data=f"host_field_set:alpn:{alpn}")])
        keyboard.append([InlineKeyboardButton("🗑️ Очистить", callback_data=f"host_field_clear:alpn")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")])
        
    elif field == 'fingerprint':
        current = host.get('fingerprint') or 'Не указан'
        text = f"""
✏️ <b>Редактирование Fingerprint (Отпечаток)</b>

<b>Текущее значение:</b> <code>{current}</code>

Выберите новое значение:
        """
        fp_values = [e.value for e in Fingerprint]
        keyboard = []
        for fp in fp_values:
            emoji = "✅" if fp == current else "◽"
            keyboard.append([InlineKeyboardButton(f"{emoji} {fp}", callback_data=f"host_field_set:fingerprint:{fp}")])
        keyboard.append([InlineKeyboardButton("🗑️ Очистить", callback_data=f"host_field_clear:fingerprint")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")])
        
    elif field == 'security_layer':
        current = host.get('securityLayer') or 'DEFAULT'
        text = f"""
✏️ <b>Редактирование Security Layer</b>

<b>Текущее значение:</b> <code>{current}</code>

Выберите новое значение:
        """
        sl_values = [e.value for e in SecurityLayer]
        keyboard = []
        for sl in sl_values:
            emoji = "✅" if sl == current else "◽"
            keyboard.append([InlineKeyboardButton(f"{emoji} {sl}", callback_data=f"host_field_set:security_layer:{sl}")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"host_edit_cancel")])
    
    else:
        await query.edit_message_text("❌ Неизвестное поле")
        return ConversationHandler.END
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    # Store the message ID for text input handling
    context.user_data['last_bot_message_id'] = query.message.message_id
    
    log.info(f"host_field_select returning SELECTING_FIELD for field: {field}")
    log.info(f"User data after select: {context.user_data}")
    
    # Stay in SELECTING_FIELD to handle text input
    return SELECTING_FIELD


@admin_only
async def host_field_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set field value from button selection"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    field = parts[1]
    value = parts[2]
    
    # Convert string values to appropriate types
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    
    context.user_data['field_value'] = value
    
    return await _save_field_value(update, context)


@admin_only
async def host_field_clear_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear field value (set to None)"""
    query = update.callback_query
    await query.answer()
    
    field = query.data.split(":")[1]
    context.user_data['editing_field'] = field
    context.user_data['field_value'] = None
    
    return await _save_field_value(update, context)


async def host_field_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for fields"""
    log.info("=" * 80)
    log.info("TEXT INPUT HANDLER CALLED!")
    log.info(f"Update type: {type(update)}")
    log.info(f"Has message: {update.message is not None}")
    log.info(f"Text input received: {update.message.text if update.message else 'NO MESSAGE'}")
    log.info(f"User data: {context.user_data}")
    log.info("=" * 80)
    
    field = context.user_data.get('editing_field')
    if not field:
        log.warning("No editing_field in user_data!")
        return ConversationHandler.END
    
    log.info(f"Processing text input for field: {field}")
    value = update.message.text.strip()
    context.user_data['field_value'] = value
    
    # Store message context for text input
    context.user_data['text_input_chat_id'] = update.effective_chat.id
    context.user_data['text_input_message_id'] = update.message.message_id
    
    # Delete user's message
    try:
        await update.message.delete()
        log.info("User message deleted")
    except Exception as e:
        log.error(f"Failed to delete user message: {e}")
    
    return await _save_field_value(update, context, is_text_input=True)


async def _save_field_value(update: Update, context: ContextTypes.DEFAULT_TYPE, is_text_input: bool = False):
    """Save field value to API"""
    host_uuid = context.user_data.get('editing_host_uuid')
    field = context.user_data.get('editing_field')
    value = context.user_data.get('field_value')
    host = context.user_data.get('current_host', {})
    
    if is_text_input:
        # For text input, get the last bot message that was stored
        chat_id = update.effective_chat.id
        last_message_id = context.user_data.get('last_bot_message_id')
        
        if last_message_id:
            # Edit the last bot message
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=last_message_id,
                    text="⏳ Сохранение изменений...",
                    parse_mode=ParseMode.HTML
                )
                # Create a pseudo message object for edit_target
                class PseudoMessage:
                    def __init__(self, bot, chat_id, message_id):
                        self.bot = bot
                        self.chat_id = chat_id
                        self.message_id = message_id
                    
                    async def edit_text(self, text, reply_markup=None, parse_mode=None):
                        return await self.bot.edit_message_text(
                            chat_id=self.chat_id,
                            message_id=self.message_id,
                            text=text,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode
                        )
                
                edit_target = PseudoMessage(context.bot, chat_id, last_message_id)
            except Exception as e:
                log.error(f"Failed to edit last message: {e}")
                # Send a new message if editing fails
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏳ Сохранение изменений...",
                    parse_mode=ParseMode.HTML
                )
                edit_target = msg
        else:
            # Send a new message if we don't have a stored message ID
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text="⏳ Сохранение изменений...",
                parse_mode=ParseMode.HTML
            )
            edit_target = msg
    else:
        query = update.callback_query
        await query.edit_message_text(
            "⏳ Сохранение изменений...",
            parse_mode=ParseMode.HTML
        )
        edit_target = query.message
        # Store the message ID for potential text input later
        context.user_data['last_bot_message_id'] = query.message.message_id
    
    try:
        # Prepare update data with all required fields
        update_data = {
            'uuid': host_uuid,
            'inbound_uuid': host.get('inboundUuid'),
            'remark': host.get('remark'),
            'address': host.get('address'),
            'port': host.get('port'),
        }
        
        # Map field names to API field names
        field_mapping = {
            'remark': 'remark',
            'address': 'address',
            'port': 'port',
            'is_disabled': 'is_disabled',
            'sni': 'sni',
            'host': 'host',
            'path': 'path',
            'override_sni': 'override_sni_from_address',
            'alpn': 'alpn',
            'fingerprint': 'fingerprint',
            'security_layer': 'security_layer'
        }
        
        api_field = field_mapping.get(field)
        if not api_field:
            await edit_target.edit_text(
                "❌ Неизвестное поле",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        # For enum fields, convert string to enum
        if field == 'alpn' and value:
            update_data[api_field] = ALPN(value)
        elif field == 'fingerprint' and value:
            update_data[api_field] = Fingerprint(value)
        elif field == 'security_layer' and value:
            update_data[api_field] = SecurityLayer(value)
        elif field == 'port' and value:
            # Convert port to integer
            try:
                update_data[api_field] = int(value)
            except ValueError:
                await edit_target.edit_text(
                    "❌ Порт должен быть числом",
                    parse_mode=ParseMode.HTML
                )
                return ConversationHandler.END
        else:
            update_data[api_field] = value
        
        # Update host
        await api_client.update_host(host_uuid, update_data)
        
        # Fetch updated host data
        response = await api_client.get_host(host_uuid)
        updated_host = response.get('response', {})
        context.user_data['current_host'] = updated_host
        
        # Show updated edit menu
        text = "✅ <b>Изменения сохранены!</b>\n\n" + _format_edit_menu(updated_host)
        keyboard = _build_edit_keyboard(host_uuid)
        
        result = await edit_target.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        # Update stored message ID
        if hasattr(result, 'message_id'):
            context.user_data['last_bot_message_id'] = result.message_id
        
        return SELECTING_FIELD
        
    except RemnaWaveAPIError as e:
        log.error(f"Error updating host field: {e}")
        await edit_target.edit_text(
            f"❌ <b>Ошибка при сохранении:</b>\n{str(e)}",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error saving host field")
        await edit_target.edit_text(
            f"❌ <b>Произошла ошибка:</b>\n{str(e)}",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def host_edit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing and return to host view"""
    query = update.callback_query
    await query.answer()
    
    host_uuid = context.user_data.get('editing_host_uuid')
    
    if not host_uuid:
        await query.edit_message_text(
            "❌ Ошибка: UUID хоста не найден",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Clear user data
    context.user_data.clear()
    
    # Redirect to host view
    try:
        response = await api_client.get_host(host_uuid)
        host = response.get('response', {})
        
        from . import formatters as host_fmt
        from . import keyboards as host_kb
        
        text = host_fmt.format_host_full(host)
        
        await query.edit_message_text(
            text,
            reply_markup=host_kb.host_actions(host_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.exception("Error returning to host view")
        await query.edit_message_text(
            "❌ Произошла ошибка",
            parse_mode=ParseMode.HTML
        )
    
    return ConversationHandler.END


def _format_edit_menu(host: dict) -> str:
    """Format edit menu with current values"""
    remark = host.get('remark') or 'N/A'
    address = host.get('address') or '❌ Не указан'
    port = host.get('port') or '❌'
    is_disabled = host.get('isDisabled', False)
    status = '🔴 Отключен' if is_disabled else '🟢 Активен'
    
    sni = host.get('sni') or '❌ Не указан'
    host_field = host.get('host') or '❌ Не указан'
    path = host.get('path') or '❌ Не указан'
    override_sni = '✅ Включено' if host.get('overrideSniFromAddress') else '❌ Выключено'
    alpn = host.get('alpn') or '❌ Не указан'
    fingerprint = host.get('fingerprint') or '❌ Не указан'
    security_layer = host.get('securityLayer') or 'DEFAULT'
    
    text = f"""
✏️ <b>Редактирование хоста:</b> {remark}

📋 <b>Основные настройки:</b>
<b>Примечание:</b> <code>{remark}</code>
<b>Адрес:</b> <code>{address}</code>
<b>Порт:</b> <code>{port}</code>
<b>Видимость:</b> {status}

� <b>Расширенные настройки:</b>
<b>SNI:</b> <code>{sni}</code>
<b>Host:</b> <code>{host_field}</code>
<b>Path:</b> <code>{path}</code>
<b>Переопределить SNI:</b> {override_sni}
<b>ALPN:</b> <code>{alpn}</code>
<b>Fingerprint:</b> <code>{fingerprint}</code>
<b>Security Layer:</b> <code>{security_layer}</code>

Выберите поле для редактирования:
    """
    return text.strip()


def _build_edit_keyboard(host_uuid: str) -> InlineKeyboardMarkup:
    """Build keyboard for field selection"""
    keyboard = [
        [InlineKeyboardButton("📝 Примечание", callback_data=f"host_edit_field:remark")],
        [InlineKeyboardButton("🌐 Адрес", callback_data=f"host_edit_field:address")],
        [InlineKeyboardButton("🔌 Порт", callback_data=f"host_edit_field:port")],
        [InlineKeyboardButton("👁️ Видимость", callback_data=f"host_edit_field:is_disabled")],
        [InlineKeyboardButton("─────── Расширенные ───────", callback_data=f"host_edit_noop")],
        [InlineKeyboardButton("📝 SNI", callback_data=f"host_edit_field:sni")],
        [InlineKeyboardButton("🌐 Host", callback_data=f"host_edit_field:host")],
        [InlineKeyboardButton("📁 Path", callback_data=f"host_edit_field:path")],
        [InlineKeyboardButton("🔄 Переопределить SNI", callback_data=f"host_edit_field:override_sni")],
        [InlineKeyboardButton("🔐 ALPN", callback_data=f"host_edit_field:alpn")],
        [InlineKeyboardButton("🔏 Fingerprint", callback_data=f"host_edit_field:fingerprint")],
        [InlineKeyboardButton("🛡️ Security Layer", callback_data=f"host_edit_field:security_layer")],
        [InlineKeyboardButton("✅ Готово", callback_data=f"host_edit_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def host_edit_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop button (separator) - just answer the callback"""
    query = update.callback_query
    if query:
        await query.answer()
    return SELECTING_FIELD


def create_host_edit_conversation() -> ConversationHandler:
    """Create ConversationHandler for host editing"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(host_edit_start, pattern="^host_edit:")
        ],
        states={
            SELECTING_FIELD: [
                CallbackQueryHandler(host_field_select, pattern="^host_edit_field:"),
                CallbackQueryHandler(host_edit_noop, pattern="^host_edit_noop$"),
                CallbackQueryHandler(host_edit_cancel, pattern="^host_edit_cancel$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, host_field_text_input),
            ],
            EDITING_FIELD: [
                CallbackQueryHandler(host_field_set_value, pattern="^host_field_set:"),
                CallbackQueryHandler(host_field_clear_value, pattern="^host_field_clear:"),
                CallbackQueryHandler(host_edit_cancel, pattern="^host_edit_cancel$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, host_field_text_input),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(host_edit_cancel, pattern="^host_edit_cancel$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
    )
