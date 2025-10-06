"""
HWID management handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as hwid_kb
from . import formatters as hwid_fmt


@admin_only
async def hwid_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show HWID management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
📱 <b>Управление устройствами</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=hwid_kb.hwid_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def hwid_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show devices list with interactive buttons"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка устройств...",
            parse_mode=ParseMode.HTML
        )
        
        response = await api_client.get_devices()
        devices = response.get('response', [])
        
        if not devices:
            text = "📱 <b>Список устройств</b>\n\nУстройства не найдены"
            keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        else:
            text = f"📱 <b>Список устройств</b>\n"
            text += f"<i>Всего: {len(devices)} устройств</i>\n\n"
            text += "Выберите устройство для управления:"
            
            # Build keyboard with device buttons
            keyboard = []
            for device in devices:
                hwid = device.get('hwid', 'N/A')
                username = device.get('username', 'N/A')
                
                # Truncate HWID for display
                short_hwid = hwid[:16] + '...' if len(hwid) > 16 else hwid
                button_text = f"📱 {username} | {short_hwid}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"device_view:{hwid}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching devices: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка:</b>\n{str(e)}",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in devices list")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def device_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed device information"""
    query = update.callback_query
    await query.answer()
    
    try:
        hwid = query.data.split(":", 1)[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch device details
        response = await api_client.get_device(hwid)
        device = response.get('response', {})
        
        if not device:
            await query.edit_message_text(
                "❌ Устройство не найдено",
                reply_markup=hwid_kb.hwid_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Format device info
        text = hwid_fmt.format_device_full(device)
        
        await query.edit_message_text(
            text,
            reply_markup=hwid_kb.device_actions(hwid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching device: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in device view")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def device_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete device"""
    query = update.callback_query
    await query.answer()
    
    try:
        hwid = query.data.split(":", 1)[1]
        
        await query.edit_message_text(
            "⏳ Удаление устройства...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.delete_device(hwid)
        
        await query.edit_message_text(
            "✅ <b>Устройство успешно удалено</b>",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error deleting device: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при удалении:</b>\n{str(e)}",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in device delete")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=hwid_kb.hwid_menu(),
            parse_mode=ParseMode.HTML
        )


def register_hwid_handlers(application):
    """Register all HWID management handlers"""
    application.add_handler(CallbackQueryHandler(hwid_menu_callback, pattern="^hwid_menu$"))
    application.add_handler(CallbackQueryHandler(hwid_list_callback, pattern="^hwid_list$"))
    application.add_handler(CallbackQueryHandler(device_view_callback, pattern="^device_view:"))
    application.add_handler(CallbackQueryHandler(device_delete_callback, pattern="^device_delete:"))
    
    log.info("✅ HWID feature handlers registered")
