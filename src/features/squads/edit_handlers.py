"""
Handlers for squad editing and user management
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from src.core.logger import log
from . import keyboards as squad_kb
from . import formatters as squad_fmt


@admin_only
async def squad_add_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add users to squad - shows options"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        # Get squad info
        response = await api_client.get_squad(squad_uuid)
        squad = response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        text = f"""
👥 <b>Добавление пользователей в отряд "{squad_name}"</b>

Выберите действие:
        """
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить ВСЕХ пользователей", callback_data=f"squad_add_all:{squad_uuid}")],
            [InlineKeyboardButton("◀️ Назад к отряду", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in squad add users: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squad add users")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_remove_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove users from squad - shows options"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        # Get squad info
        response = await api_client.get_squad(squad_uuid)
        squad = response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        text = f"""
👥 <b>Удаление пользователей из отряда "{squad_name}"</b>

Выберите действие:
        """
        
        keyboard = [
            [InlineKeyboardButton("➖ Удалить ВСЕХ пользователей", callback_data=f"squad_remove_all:{squad_uuid}")],
            [InlineKeyboardButton("◀️ Назад к отряду", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in squad remove users: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squad remove users")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_accessible_nodes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show accessible nodes for squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка доступных нод...",
            parse_mode=ParseMode.HTML
        )
        
        # Get squad info
        squad_response = await api_client.get_squad(squad_uuid)
        squad = squad_response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        # Get accessible nodes
        response = await api_client.get_squad_accessible_nodes(squad_uuid)
        nodes = response.get('response', [])
        
        if not nodes:
            text = f"📡 <b>Доступные ноды для отряда \"{squad_name}\"</b>\n\nДоступных нод нет"
        else:
            text = f"📡 <b>Доступные ноды для отряда \"{squad_name}\"</b>\n\n"
            text += f"<i>Всего: {len(nodes)} нод</i>\n\n"
            
            for node in nodes:
                name = node.get('name', 'N/A')
                address = node.get('address', 'N/A')
                is_disabled = node.get('isDisabled', False)
                status_emoji = '🔴' if is_disabled else '🟢'
                text += f"{status_emoji} <b>{name}</b> | {address}\n"
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к отряду", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error getting squad accessible nodes: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squad accessible nodes")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_add_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add all users to squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Добавление всех пользователей в отряд...",
            parse_mode=ParseMode.HTML
        )
        
        # Get squad info
        squad_response = await api_client.get_squad(squad_uuid)
        squad = squad_response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        # API automatically adds ALL users
        await api_client.add_users_to_squad(squad_uuid)
        
        text = f"""
✅ <b>Успешно добавлено!</b>

Все пользователи добавлены в отряд "{squad_name}"
        """
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к отряду", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error adding all users to squad: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error adding all users to squad")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_remove_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all users from squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Удаление всех пользователей из отряда...",
            parse_mode=ParseMode.HTML
        )
        
        # Get squad info
        squad_response = await api_client.get_squad(squad_uuid)
        squad = squad_response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        # API automatically removes ALL users
        await api_client.remove_users_from_squad(squad_uuid)
        
        text = f"""
✅ <b>Успешно удалено!</b>

Все пользователи удалены из отряда "{squad_name}"
        """
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к отряду", callback_data=f"squad_view:{squad_uuid}")],
            [InlineKeyboardButton("◀️ К списку отрядов", callback_data="squads_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error removing all users from squad: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error removing all users from squad")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
