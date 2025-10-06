"""
Node management keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def nodes_menu() -> InlineKeyboardMarkup:
    """Nodes management menu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Список нод", callback_data="nodes_list"),
        ],
        [
            InlineKeyboardButton("➕ Добавить ноду", callback_data="node_create"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def node_actions(node_uuid: str) -> InlineKeyboardMarkup:
    """Node action buttons"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"node_edit:{node_uuid}"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"node_stats:{node_uuid}"),
        ],
        [
            InlineKeyboardButton("🔄 Перезапустить", callback_data=f"node_restart:{node_uuid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"node_delete:{node_uuid}"),
        ],
        [
            InlineKeyboardButton("◀️ К списку", callback_data="nodes_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
