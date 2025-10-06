"""
HWID management keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def hwid_menu() -> InlineKeyboardMarkup:
    """HWID management menu"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Список устройств", callback_data="hwid_list"),
        ],
        [
            InlineKeyboardButton("🔍 Поиск по HWID", callback_data="hwid_search"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def device_actions(device_id: str) -> InlineKeyboardMarkup:
    """Device action buttons"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика", callback_data=f"device_stats:{device_id}"),
        ],
        [
            InlineKeyboardButton("🔓 Разблокировать", callback_data=f"device_unlock:{device_id}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"device_delete:{device_id}"),
        ],
        [
            InlineKeyboardButton("◀️ К списку", callback_data="hwid_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
