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
            # Calculate total statistics
            total_traffic_used = 0
            total_traffic_limit = 0
            total_users = 0
            active_nodes = 0
            
            for node in nodes:
                if not node.get('isDisabled', False):
                    active_nodes += 1
                total_traffic_used += node.get('trafficUsedBytes', 0)
                total_traffic_limit += node.get('trafficLimitBytes', 0)
                total_users += len(node.get('users', []))
            
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
            
            total_used_str = format_bytes(total_traffic_used)
            total_limit_str = format_bytes(total_traffic_limit) if total_traffic_limit else "Не установлен"
            
            text = f"📡 <b>Список нод</b>\n\n"
            text += f"📊 <b>Статистика:</b>\n"
            text += f"🟢 Активных: {active_nodes} / {len(nodes)}\n"
            text += f"👥 Пользователей: {total_users}\n"
            text += f"📥 Потреблено: {total_used_str}\n"
            if total_traffic_limit:
                usage_percent = (total_traffic_used / total_traffic_limit) * 100
                text += f"📊 Лимит: {total_limit_str} ({usage_percent:.1f}%)\n"
            text += f"\n<i>Выберите ноду для управления:</i>"
            
            # Build keyboard with node buttons
            keyboard = []
            for node in nodes:
                name = node.get('name', 'N/A')
                address = node.get('address', 'N/A')
                port = node.get('port', 'N/A')
                uuid = node.get('uuid', '')
                is_disabled = node.get('isDisabled', False)
                users_count = len(node.get('users', []))
                traffic_used = node.get('trafficUsedBytes', 0)
                
                status_emoji = '🔴' if is_disabled else '🟢'
                traffic_str = format_bytes(traffic_used)
                button_text = f"{status_emoji} {name} | 👥{users_count} | 📥{traffic_str}"
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
        is_disabled = node.get('isDisabled', False)
        
        await query.edit_message_text(
            text,
            reply_markup=node_kb.node_actions(node_uuid, is_disabled),
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





def register_nodes_handlers(application):
    """Register all node management handlers"""
    from .edit_handlers import (
        node_edit_start,
        node_field_select,
        node_text_input_handler,
        node_edit_done
    )
    from .actions_handlers import (
        node_stats_callback,
        node_restart_callback,
        node_toggle_callback,
        node_delete_start,
        node_delete_confirm_handler,
        node_delete_cancel
    )
    
    # Main handlers
    application.add_handler(CallbackQueryHandler(nodes_menu_callback, pattern="^nodes_menu$"))
    application.add_handler(CallbackQueryHandler(nodes_list_callback, pattern="^nodes_list$"))
    application.add_handler(CallbackQueryHandler(node_view_callback, pattern="^node_view:"))
    
    # Edit handlers
    application.add_handler(CallbackQueryHandler(node_edit_start, pattern="^node_edit:"))
    application.add_handler(CallbackQueryHandler(node_field_select, pattern="^node_edit_field:"))
    application.add_handler(CallbackQueryHandler(node_edit_done, pattern="^node_edit_done$"))
    
    # Action handlers
    application.add_handler(CallbackQueryHandler(node_stats_callback, pattern="^node_stats:"))
    application.add_handler(CallbackQueryHandler(node_restart_callback, pattern="^node_restart:"))
    application.add_handler(CallbackQueryHandler(node_toggle_callback, pattern="^node_enable:"))
    application.add_handler(CallbackQueryHandler(node_toggle_callback, pattern="^node_disable:"))
    application.add_handler(CallbackQueryHandler(node_delete_start, pattern="^node_delete:"))
    application.add_handler(CallbackQueryHandler(node_delete_cancel, pattern="^node_delete_cancel:"))
    
    # Combined text handler for node editing and delete confirmation
    from telegram.ext import MessageHandler, filters
    
    async def combined_text_handler(update, context):
        if context.user_data.get('waiting_text_input', {}).get('type') == 'node_edit':
            await node_text_input_handler(update, context)
        elif context.user_data.get('delete_node_confirmation'):
            await node_delete_confirm_handler(update, context)
    
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            combined_text_handler
        ),
        group=1
    )
    
    log.info("✅ Nodes feature handlers registered")
