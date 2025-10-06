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


def node_actions(node_uuid: str, is_disabled: bool = False) -> InlineKeyboardMarkup:
    """Node action buttons"""
    # Toggle button text based on current state
    toggle_text = "🟢 Включить" if is_disabled else "🔴 Выключить"
    toggle_action = "node_enable" if is_disabled else "node_disable"
    
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"node_edit:{node_uuid}"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"node_stats:{node_uuid}"),
        ],
        [
            InlineKeyboardButton("🔄 Перезапустить", callback_data=f"node_restart:{node_uuid}"),
            InlineKeyboardButton(toggle_text, callback_data=f"{toggle_action}:{node_uuid}"),
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
