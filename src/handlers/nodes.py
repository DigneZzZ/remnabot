"""
Nodes management handlers
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards
from src.utils.formatters import formatters
from src.services.api import api_client, RemnaWaveAPIError


@admin_only
async def nodes_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show nodes management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🌐 <b>Управление нодами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=keyboards.nodes_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def nodes_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show nodes list"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка нод...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_nodes()
        # API returns data in 'response' wrapper
        nodes = response.get('response', []) if isinstance(response, dict) else response
        
        if not nodes:
            text = "🌐 <b>Список нод</b>\n\nНоды не найдены"
        else:
            text = "🌐 <b>Список нод</b>\n\n"
            for node in nodes:
                text += formatters.format_node(node) + "\n\n"
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=keyboards.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching nodes: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка нод:</b>\n{str(e)}",
            reply_markup=keyboards.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in nodes list callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def node_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show node statistics"""
    query = update.callback_query
    await query.answer()
    
    node_uuid = query.data.split(":")[1]
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка статистики ноды...",
            parse_mode=ParseMode.HTML
        )
        
        node = await api_client.get_node(node_uuid)
        stats = await api_client.get_node_stats(node_uuid)
        
        text = formatters.format_node_stats(node, stats)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboards.node_actions(node_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching node stats: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении статистики:</b>\n{str(e)}",
            reply_markup=keyboards.nodes_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in node stats callback")
        await query.edit_message_text(
            "❌ <b>Произошла непредвиденная ошибка</b>",
            reply_markup=keyboards.nodes_menu(),
            parse_mode=ParseMode.HTML
        )


def register_nodes_handlers(application):
    """Register nodes management handlers"""
    application.add_handler(CallbackQueryHandler(nodes_menu_callback, pattern="^nodes_menu$"))
    application.add_handler(CallbackQueryHandler(nodes_list_callback, pattern="^nodes_list$"))
    application.add_handler(CallbackQueryHandler(node_stats_callback, pattern="^node_stats:"))
    
    log.info("Nodes handlers registered")
