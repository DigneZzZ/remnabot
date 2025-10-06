"""
Squad management keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def squads_menu() -> InlineKeyboardMarkup:
    """Squads management menu"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Список отрядов", callback_data="squads_list"),
        ],
        [
            InlineKeyboardButton("➕ Создать отряд", callback_data="squad_create"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def squad_actions(squad_uuid: str) -> InlineKeyboardMarkup:
    """Squad action buttons"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"squad_edit:{squad_uuid}"),
            InlineKeyboardButton("👤 Участники", callback_data=f"squad_members:{squad_uuid}"),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data=f"squad_stats:{squad_uuid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"squad_delete:{squad_uuid}"),
        ],
        [
            InlineKeyboardButton("◀️ К списку", callback_data="squads_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
