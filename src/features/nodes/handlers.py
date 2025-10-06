"""
Node management handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as node_kb
from . import formatters as node_fmt


@admin_only
async def nodes_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show nodes management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
📡 <b>Управление нодами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=node_kb.nodes_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def nodes_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show nodes list with interactive buttons"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка нод...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_nodes()
        nodes = response.get('response', [])
        
        if not nodes:
            text = "📡 <b>Список нод</b>\n\nНоды не найдены"
            keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        else:
            text = f"📡 <b>Список нод</b>\n"
            text += f"<i>Всего: {len(nodes)} нод</i>\n\n"
            text += "Выберите ноду для управления:"
            
            # Build keyboard with node buttons
            keyboard = []
            for node in nodes:
                name = node.get('name', 'N/A')
                address = node.get('address', 'N/A')
                port = node.get('port', 'N/A')
                uuid = node.get('uuid', '')
                is_disabled = node.get('isDisabled', False)
                
                status_emoji = '🔴' if is_disabled else '🟢'
                button_text = f"{status_emoji} {name} | {address}:{port}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"node_view:{uuid}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching nodes: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in nodes list")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed node information"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch node details
        response = await api_client.get_node(node_uuid)
        node = response.get('response', {})
        
        if not node:
            await query.edit_message_text(
                "❌ Нода не найдена",
                reply_markup=node_kb.nodes_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format node info
        text = node_fmt.format_node_full(node)
        
        await query.edit_message_text(
            text,
            reply_markup=node_kb.node_actions(node_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching node: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node view")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete node"""
    query = update.callback_query
    await query.answer()
    
    try:
        node_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Удаление ноды...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.delete_node(node_uuid)
        
        await query.edit_message_text(
            "✅ <b>Нода успешно удалена</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error deleting node: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при удалении:</b>\n{str(e)}",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node delete")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=node_kb.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


def register_nodes_handlers(application):
    """Register all node management handlers"""
    application.add_handler(CallbackQueryHandler(nodes_menu_callback, pattern="^nodes_menu$"))
    application.add_handler(CallbackQueryHandler(nodes_list_callback, pattern="^nodes_list$"))
    application.add_handler(CallbackQueryHandler(node_view_callback, pattern="^node_view:"))
    application.add_handler(CallbackQueryHandler(node_delete_callback, pattern="^node_delete:"))
    
    log.info("✅ Nodes feature handlers registered")
