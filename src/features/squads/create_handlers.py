"""
Handlers for squad creation
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from src.core.logger import log
from . import keyboards as squad_kb

# Conversation states
SQUAD_NAME, SQUAD_INBOUNDS = range(2)


@admin_only
async def squad_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start squad creation process"""
    query = update.callback_query
    await query.answer()
    
    # Clear any previous state
    context.user_data.clear()
    
    text = """
👥 <b>Создание нового отряда</b>

Шаг 1️⃣: Введите название отряда

Название должно быть уникальным и понятным.

<i>Отправьте /cancel для отмены</i>
    """
    
    await query.edit_message_text(
        text.strip(),
        parse_mode=ParseMode.HTML
    )
    
    return SQUAD_NAME


@admin_only
async def squad_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle squad name input"""
    if not update.message or not update.message.text:
        return SQUAD_NAME
    
    squad_name = update.message.text.strip()
    
    if len(squad_name) < 2:
        await update.message.reply_text(
            "❌ Название должно содержать минимум 2 символа.\n"
            "Попробуйте еще раз или отправьте /cancel для отмены.",
            parse_mode=ParseMode.HTML
        )
        return SQUAD_NAME
    
    # Save name in context
    context.user_data['squad_name'] = squad_name
    
    # Get available inbounds
    try:
        response = await api_client.get_inbounds()
        inbounds = response.get('response', [])
        
        if not inbounds:
            await update.message.reply_text(
                "❌ <b>Inbound'ы не найдены</b>\n\n"
                "Сначала создайте хотя бы один inbound.",
                reply_markup=squad_kb.squads_menu(),
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        # Build keyboard with inbounds
        keyboard = []
        for inbound in inbounds:
            tag = inbound.get('tag', 'N/A')
            protocol = inbound.get('protocol', 'N/A')
            uuid = inbound.get('uuid', '')
            
            button_text = f"📡 {tag} ({protocol})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"squad_create_inbound:{uuid}")])
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="squad_create_cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
👥 <b>Создание отряда "{squad_name}"</b>

Шаг 2️⃣: Выберите inbound для отряда

Выберите inbound, к которому будут привязаны пользователи этого отряда.
        """
        
        await update.message.reply_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return SQUAD_INBOUNDS
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching inbounds: {e}")
        await update.message.reply_text(
            f"❌ <b>Ошибка при получении inbound'ов:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def squad_create_inbound_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inbound selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        inbound_uuid = query.data.split(":")[1]
        squad_name = context.user_data.get('squad_name')
        
        if not squad_name:
            await query.edit_message_text(
                "❌ <b>Ошибка:</b> данные сессии потеряны.\n"
                "Попробуйте создать отряд заново.",
                reply_markup=squad_kb.squads_menu(),
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        # Create squad
        await query.edit_message_text(
            f"⏳ Создание отряда <b>{squad_name}</b>...",
            parse_mode=ParseMode.HTML
        )
        
        squad_data = {
            'name': squad_name,
            'inbounds': [inbound_uuid]
        }
        
        response = await api_client.create_squad(squad_data)
        squad = response.get('response', {})
        squad_uuid = squad.get('uuid', 'N/A')
        
        keyboard = [
            [InlineKeyboardButton("👁️ Просмотреть отряд", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ <b>Отряд успешно создан!</b>\n\n"
            f"<b>Название:</b> {squad_name}\n"
            f"<b>UUID:</b> <code>{squad_uuid}</code>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        # Clear context
        context.user_data.clear()
        return ConversationHandler.END
        
    except RemnaWaveAPIError as e:
        log.error(f"Error creating squad: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при создании отряда:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error in squad creation")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def squad_create_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel squad creation"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ Создание отряда отменено",
        reply_markup=squad_kb.squads_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END


@admin_only
async def squad_create_conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command during conversation"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Создание отряда отменено",
        reply_markup=squad_kb.squads_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END
