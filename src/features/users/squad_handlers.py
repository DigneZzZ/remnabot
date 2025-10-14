"""
Handlers for managing user squads
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError
from src.core.logger import log


@admin_only
async def user_squads_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user squads management menu"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        context.user_data['managing_squads_for_user'] = user_uuid
        
        # Get user info
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        username = user.get('username', 'N/A')
        current_squads = user.get('activeInternalSquads', [])
        
        # Get all available squads
        squads_response = await api_client.get_squads()
        response_data = squads_response.get('response', {})
        all_squads = response_data.get('internalSquads', [])
        
        if not all_squads:
            text = f"""
👥 <b>Управление отрядами пользователя</b>

Пользователь: <code>{username}</code>

В системе нет доступных отрядов.
            """
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data=f"user_view:{user_uuid}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text.strip(),
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            return
        
        # Build message
        text = f"""
👥 <b>Управление отрядами пользователя</b>

Пользователь: <code>{username}</code>

<b>Текущие отряды:</b>
"""
        
        if current_squads:
            for squad_uuid in current_squads:
                squad = next((s for s in all_squads if s.get('uuid') == squad_uuid), None)
                if squad:
                    text += f"✅ {squad.get('name', 'N/A')}\n"
        else:
            text += "Нет назначенных отрядов\n"
        
        text += "\n<b>Доступные отряды:</b>\n"
        
        # Build keyboard with squad buttons
        keyboard = []
        for squad in all_squads:
            squad_uuid = squad.get('uuid')
            squad_name = squad.get('name', 'N/A')
            
            if squad_uuid in current_squads:
                # Squad is already assigned - show remove button
                button_text = f"➖ {squad_name}"
                callback_data = f"user_squad_remove:{user_uuid}:{squad_uuid}"
            else:
                # Squad is not assigned - show add button  
                button_text = f"➕ {squad_name}"
                callback_data = f"user_squad_add:{user_uuid}:{squad_uuid}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("◀️ Назад к пользователю", callback_data=f"user_view:{user_uuid}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error in user squads menu: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in user squads menu")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_squad_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user to squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        _, user_uuid, squad_uuid = query.data.split(":")
        
        # Get user info
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        username = user.get('username', 'N/A')
        current_squads = user.get('activeInternalSquads', []) or []
        
        # Get squad info
        squad_response = await api_client.get_squad(squad_uuid)
        squad = squad_response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        # Add squad to user's list
        if squad_uuid not in current_squads:
            current_squads.append(squad_uuid)
        
        # Update user
        update_data = {'activeInternalSquads': current_squads}
        await api_client.update_user(user_uuid, update_data)
        
        await query.answer(f"✅ Добавлен в отряд '{squad_name}'", show_alert=True)
        
        # Refresh the menu
        context.matches = [type('obj', (object,), {'group': lambda x: f"user_squads:{user_uuid}"})]
        query.data = f"user_squads:{user_uuid}"
        await user_squads_menu(update, context)
        
    except RemnaWaveAPIError as e:
        log.error(f"Error adding user to squad: {e}")
        await query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    except Exception as e:
        log.exception("Unexpected error adding user to squad")
        await query.answer("❌ Произошла ошибка", show_alert=True)


@admin_only
async def user_squad_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user from squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        _, user_uuid, squad_uuid = query.data.split(":")
        
        # Get user info
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        username = user.get('username', 'N/A')
        current_squads = user.get('activeInternalSquads', []) or []
        
        # Get squad info
        squad_response = await api_client.get_squad(squad_uuid)
        squad = squad_response.get('response', {})
        squad_name = squad.get('name', 'N/A')
        
        # Remove squad from user's list
        if squad_uuid in current_squads:
            current_squads.remove(squad_uuid)
        
        # Update user
        update_data = {'activeInternalSquads': current_squads}
        await api_client.update_user(user_uuid, update_data)
        
        await query.answer(f"✅ Удален из отряда '{squad_name}'", show_alert=True)
        
        # Refresh the menu
        context.matches = [type('obj', (object,), {'group': lambda x: f"user_squads:{user_uuid}"})]
        query.data = f"user_squads:{user_uuid}"
        await user_squads_menu(update, context)
        
    except RemnaWaveAPIError as e:
        log.error(f"Error removing user from squad: {e}")
        await query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    except Exception as e:
        log.exception("Unexpected error removing user from squad")
        await query.answer("❌ Произошла ошибка", show_alert=True)
