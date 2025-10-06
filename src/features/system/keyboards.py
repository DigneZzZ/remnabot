"""
System keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def system_menu() -> InlineKeyboardMarkup:
    """System management menu"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика системы", callback_data="system_stats"),
        ],
        [
            InlineKeyboardButton("🔄 Перезапустить Xray", callback_data="system_restart_xray"),
        ],
        [
            InlineKeyboardButton("🗑️ Очистить логи", callback_data="system_clear_logs"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
