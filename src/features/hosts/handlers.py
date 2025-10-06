"""
Host management handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as host_kb
from . import formatters as host_fmt


@admin_only
async def hosts_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hosts management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🖥️ <b>Управление хостами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=host_kb.hosts_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def hosts_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hosts list with interactive buttons"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка хостов...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_hosts()
        hosts = response.get('response', [])
        
        if not hosts:
            text = "🖥️ <b>Список хостов</b>\n\nХосты не найдены"
            keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        else:
            text = f"🖥️ <b>Список хостов</b>\n"
            text += f"<i>Всего: {len(hosts)} хостов</i>\n\n"
            text += "Выберите хост для управления:"
            
            # Build keyboard with host buttons
            keyboard = []
            for host in hosts:
                remark = host.get('remark', 'N/A')
                address = host.get('address', 'N/A')
                port = host.get('port', 'N/A')
                uuid = host.get('uuid', '')
                is_disabled = host.get('isDisabled', False)
                
                status_emoji = '🔴' if is_disabled else '🟢'
                button_text = f"{status_emoji} {remark} | {address}:{port}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"host_view:{uuid}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching hosts: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка:</b>\n{str(e)}",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in hosts list")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def host_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed host information"""
    query = update.callback_query
    await query.answer()
    
    try:
        host_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch host details
        response = await api_client.get_host(host_uuid)
        host = response.get('response', {})
        
        if not host:
            await query.edit_message_text(
                "❌ Хост не найден",
                reply_markup=host_kb.hosts_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format host info
        text = host_fmt.format_host_full(host)
        
        await query.edit_message_text(
            text,
            reply_markup=host_kb.host_actions(host_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching host: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in host view")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def host_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete host"""
    query = update.callback_query
    await query.answer()
    
    try:
        host_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Удаление хоста...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.delete_host(host_uuid)
        
        await query.edit_message_text(
            "✅ <b>Хост успешно удален</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error deleting host: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при удалении:</b>\n{str(e)}",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in host delete")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=host_kb.hosts_menu(),
            parse_mode=ParseMode.HTML
        )


def register_hosts_handlers(application):
    """Register all host management handlers"""
    application.add_handler(CallbackQueryHandler(hosts_menu_callback, pattern="^hosts_menu$"))
    application.add_handler(CallbackQueryHandler(hosts_list_callback, pattern="^hosts_list$"))
    application.add_handler(CallbackQueryHandler(host_view_callback, pattern="^host_view:"))
    application.add_handler(CallbackQueryHandler(host_delete_callback, pattern="^host_delete:"))
    
    log.info("✅ Hosts feature handlers registered")
