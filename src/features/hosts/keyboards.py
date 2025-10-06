"""
Host management keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


def hosts_menu() -> InlineKeyboardMarkup:
    """Hosts management menu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Список хостов", callback_data="hosts_list"),
        ],
        [
            InlineKeyboardButton("➕ Добавить хост", callback_data="host_create"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def host_actions(host_uuid: str) -> InlineKeyboardMarkup:
    """Host action buttons"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"host_edit:{host_uuid}"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"host_stats:{host_uuid}"),
        ],
        [
            InlineKeyboardButton("🔄 Перезапустить", callback_data=f"host_restart:{host_uuid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"host_delete:{host_uuid}"),
        ],
        [
            InlineKeyboardButton("◀️ К списку", callback_data="hosts_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
