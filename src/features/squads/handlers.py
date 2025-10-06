"""
Squad management handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as squad_kb
from . import formatters as squad_fmt


@admin_only
async def squads_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show squads management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
👥 <b>Управление отрядами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=squad_kb.squads_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def squads_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show squads list with interactive buttons"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка отрядов...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_squads()
        squads = response.get('response', [])
        
        if not squads:
            text = "👥 <b>Список отрядов</b>\n\nОтряды не найдены"
            keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        else:
            text = f"👥 <b>Список отрядов</b>\n"
            text += f"<i>Всего: {len(squads)} отрядов</i>\n\n"
            text += "Выберите отряд для управления:"
            
            # Build keyboard with squad buttons
            keyboard = []
            for squad in squads:
                name = squad.get('name', 'N/A')
                uuid = squad.get('uuid', '')
                members_count = squad.get('membersCount', 0)
                
                button_text = f"👥 {name} | {members_count} чел."
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"squad_view:{uuid}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching squads: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squads list")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed squad information"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch squad details
        response = await api_client.get_squad(squad_uuid)
        squad = response.get('response', {})
        
        if not squad:
            await query.edit_message_text(
                "❌ Отряд не найден",
                reply_markup=squad_kb.squads_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format squad info
        text = squad_fmt.format_squad_full(squad)
        
        await query.edit_message_text(
            text,
            reply_markup=squad_kb.squad_actions(squad_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching squad: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squad view")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def squad_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete squad"""
    query = update.callback_query
    await query.answer()
    
    try:
        squad_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Удаление отряда...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.delete_squad(squad_uuid)
        
        await query.edit_message_text(
            "✅ <b>Отряд успешно удален</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error deleting squad: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при удалении:</b>\n{str(e)}",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in squad delete")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=squad_kb.squads_menu(),
            parse_mode=ParseMode.HTML
        )


def register_squads_handlers(application):
    """Register all squad management handlers"""
    application.add_handler(CallbackQueryHandler(squads_menu_callback, pattern="^squads_menu$"))
    application.add_handler(CallbackQueryHandler(squads_list_callback, pattern="^squads_list$"))
    application.add_handler(CallbackQueryHandler(squad_view_callback, pattern="^squad_view:"))
    application.add_handler(CallbackQueryHandler(squad_delete_callback, pattern="^squad_delete:"))
    
    log.info("✅ Squads feature handlers registered")
