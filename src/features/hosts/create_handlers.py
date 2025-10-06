"""
Host creation handlers - Simple wizard-style approach
Collects required fields step by step, then creates host
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client
from src.core.logger import log
from remnawave.enums import ALPN, Fingerprint, SecurityLayer
from remnawave.models.hosts import CreateHostRequestDto, CreateHostInboundData


@admin_only
async def host_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start host creation wizard"""
    query = update.callback_query
    await query.answer()
    
    # Initialize creation data
    context.user_data['creating_host'] = {
        'step': 'remark',  # Current step
        'data': {}  # Collected data
    }
    
    text = """
🆕 <b>Создание нового хоста</b>

Шаг 1/4: <b>Примечание</b>

Введите примечание (название хоста):
    """
    
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="host_create_cancel")]]
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def host_create_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input during host creation"""
    creation_data = context.user_data.get('creating_host')
    if not creation_data:
        return  # Not in creation mode
    
    step = creation_data['step']
    text = update.message.text.strip()
    
    log.info(f"Host creation step '{step}' received: {text}")
    
    # Delete user message
    try:
        await update.message.delete()
    except:
        pass
    
    # Get the message ID to edit (from context or send new)
    chat_id = update.effective_chat.id
    message_id = creation_data.get('message_id')
    
    # Process based on current step
    if step == 'remark':
        creation_data['data']['remark'] = text
        creation_data['step'] = 'address'
        
        new_text = f"""
🆕 <b>Создание нового хоста</b>

✅ Примечание: <code>{text}</code>

Шаг 2/4: <b>Адрес</b>

Введите адрес хоста (IP или домен):
        """
        keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="host_create_cancel")]]
        
        if message_id:
            result = await context.bot.edit_message_text(
                new_text.strip(),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        else:
            result = await context.bot.send_message(
                chat_id=chat_id,
                text=new_text.strip(),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            creation_data['message_id'] = result.message_id
    
    elif step == 'address':
        creation_data['data']['address'] = text
        creation_data['step'] = 'port'
        
        new_text = f"""
🆕 <b>Создание нового хоста</b>

✅ Примечание: <code>{creation_data['data']['remark']}</code>
✅ Адрес: <code>{text}</code>

Шаг 3/4: <b>Порт</b>

Введите порт (например, 443):
        """
        keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="host_create_cancel")]]
        
        await context.bot.edit_message_text(
            new_text.strip(),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif step == 'port':
        # Validate port
        try:
            port = int(text)
            if port < 1 or port > 65535:
                raise ValueError("Port out of range")
        except ValueError:
            await context.bot.edit_message_text(
                "❌ Ошибка: порт должен быть числом от 1 до 65535\n\nВведите корректный порт:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="host_create_cancel")]]),
                parse_mode=ParseMode.HTML
            )
            return
        
        creation_data['data']['port'] = port
        creation_data['step'] = 'inbound'
        
        # Fetch available inbounds to select from
        await _show_inbound_selection(context, chat_id, message_id, creation_data)


async def _show_inbound_selection(context, chat_id, message_id, creation_data):
    """Show inbound selection step"""
    try:
        # Fetch inbounds from API
        response = await api_client.get_inbounds()
        if not response or 'response' not in response:
            await context.bot.edit_message_text(
                "❌ Ошибка при загрузке inbounds",
                chat_id=chat_id,
                message_id=message_id
            )
            return
        
        # Get inbounds list from response
        inbounds_data = response['response']
        inbounds = inbounds_data.get('inbounds', []) if isinstance(inbounds_data, dict) else inbounds_data
        
        if not inbounds:
            await context.bot.edit_message_text(
                "❌ Нет доступных inbounds для создания хоста",
                chat_id=chat_id,
                message_id=message_id
            )
            return
        
        # Build keyboard with numbered inbounds
        keyboard = []
        inbound_list = []
        inbound_mapping = []  # Store inbound data by index
        buttons = []  # Temporary list for building rows
        
        for idx, inbound in enumerate(inbounds):
            # Get UUID fields - check both formats
            config_uuid = None
            inbound_uuid = None
            tag = 'Unknown'
            
            if isinstance(inbound, dict):
                # Try new format first
                config_uuid = inbound.get('profileUuid')
                inbound_uuid = inbound.get('uuid')
                tag = inbound.get('tag', 'Unknown')
                
                # Fallback to old format
                if not config_uuid:
                    config_uuid = inbound.get('configProfile', {}).get('uuid')
                if not inbound_uuid:
                    inbound_uuid = inbound.get('inbound', {}).get('uuid')
            
            if config_uuid and inbound_uuid:
                # Store inbound data for later use
                inbound_mapping.append({
                    'config_uuid': str(config_uuid),
                    'inbound_uuid': str(inbound_uuid),
                    'tag': tag
                })
                
                # Store for text display (1-indexed for user)
                display_idx = len(inbound_mapping)
                inbound_list.append(f"{display_idx}. {tag}")
                
                # Add button to temporary list
                buttons.append(
                    InlineKeyboardButton(
                        f"{display_idx}",
                        callback_data=f"host_create_inbound:{idx}"
                    )
                )
                
                # When we have 3 buttons, add them as a row
                if len(buttons) == 3:
                    keyboard.append(buttons)
                    buttons = []
        
        # Add remaining buttons if any
        if buttons:
            keyboard.append(buttons)
        
        # Store inbound mapping in context for callback handler
        creation_data['inbound_mapping'] = inbound_mapping
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="host_create_cancel")])
        
        # Build inbound list text
        inbound_list_text = '\n'.join(inbound_list) if inbound_list else 'Нет доступных inbounds'
        
        text = f"""
🆕 <b>Создание нового хоста</b>

✅ Примечание: <code>{creation_data['data']['remark']}</code>
✅ Адрес: <code>{creation_data['data']['address']}</code>
✅ Порт: <code>{creation_data['data']['port']}</code>

Шаг 4/4: <b>Inbound</b>

Доступные inbounds:
{inbound_list_text}

Выберите номер inbound:
        """
        
        await context.bot.edit_message_text(
            text.strip(),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error loading inbounds: {e}")
        await context.bot.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            chat_id=chat_id,
            message_id=message_id
        )


@admin_only
async def host_create_inbound_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inbound selection"""
    query = update.callback_query
    await query.answer()
    
    creation_data = context.user_data.get('creating_host')
    if not creation_data:
        await query.edit_message_text("❌ Ошибка: данные создания не найдены")
        return
    
    # Parse inbound index
    parts = query.data.split(":")
    inbound_idx = int(parts[1])
    
    # Get inbound data from mapping
    inbound_mapping = creation_data.get('inbound_mapping', [])
    if inbound_idx >= len(inbound_mapping):
        await query.edit_message_text("❌ Ошибка: неверный индекс inbound")
        return
    
    inbound_data = inbound_mapping[inbound_idx]
    
    creation_data['data']['inbound'] = {
        'config_profile_uuid': inbound_data['config_uuid'],
        'config_profile_inbound_uuid': inbound_data['inbound_uuid']
    }
    
    # Show summary and create
    await _create_host(query, context, creation_data)


async def _create_host(query, context, creation_data):
    """Create host with collected data"""
    try:
        data = creation_data['data']
        
        # Show creating message
        await query.edit_message_text(
            "⏳ Создание хоста...",
            parse_mode=ParseMode.HTML
        )
        
        # Prepare DTO
        inbound_data = CreateHostInboundData(
            config_profile_uuid=data['inbound']['config_profile_uuid'],
            config_profile_inbound_uuid=data['inbound']['config_profile_inbound_uuid']
        )
        
        create_dto = CreateHostRequestDto(
            inbound=inbound_data,
            remark=data['remark'],
            address=data['address'],
            port=data['port'],
            is_disabled=False  # Active by default
        )
        
        log.info(f"Creating host with data: {create_dto.model_dump()}")
        
        # Create host via API
        response = await api_client.create_host(create_dto)
        
        if not response or 'response' not in response:
            await query.edit_message_text(
                "❌ Ошибка при создании хоста",
                parse_mode=ParseMode.HTML
            )
            return
        
        host = response['response']
        host_uuid = host.get('uuid')
        
        # Clear creation data
        context.user_data.pop('creating_host', None)
        
        # Show success with host info
        from .formatters import format_host_full
        from .keyboards import host_actions
        
        text = f"✅ <b>Хост успешно создан!</b>\n\n{format_host_full(host)}"
        keyboard = host_actions(str(host_uuid))
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error creating host: {e}")
        await query.edit_message_text(
            f"❌ Ошибка при создании хоста: {str(e)}",
            parse_mode=ParseMode.HTML
        )


@admin_only
async def host_create_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel host creation and return to hosts menu"""
    query = update.callback_query
    await query.answer("Отменено")
    
    # Clear creation data
    context.user_data.pop('creating_host', None)
    
    # Import keyboards
    from .keyboards import hosts_menu
    
    # Return to hosts menu
    keyboard = hosts_menu()
    
    await query.edit_message_text(
        "🖥 <b>Управление хостами</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
