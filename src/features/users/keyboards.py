"""
User management keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


def users_menu() -> InlineKeyboardMarkup:
    """Users management menu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Список пользователей", callback_data="users_list"),
        ],
        [
            InlineKeyboardButton("➕ Создать пользователя", callback_data="user_create"),
            InlineKeyboardButton("📦 Массовое создание", callback_data="user_bulk_create"),
        ],
        [
            InlineKeyboardButton("🔍 Поиск пользователя", callback_data="user_search"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def user_actions(user_uuid: str) -> InlineKeyboardMarkup:
    """User action buttons"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"user_edit:{user_uuid}"),
            InlineKeyboardButton("📅 Продлить", callback_data=f"user_extend:{user_uuid}"),
        ],
        [
            InlineKeyboardButton("📱 Устройства", callback_data=f"user_devices:{user_uuid}"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"user_stats:{user_uuid}"),
        ],
        [
            InlineKeyboardButton("👥 Отряды", callback_data=f"user_squads:{user_uuid}"),
            InlineKeyboardButton("🔄 Сбросить трафик", callback_data=f"user_reset_traffic:{user_uuid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"user_delete_confirm:{user_uuid}"),
        ],
        [
            InlineKeyboardButton("◀️ К списку", callback_data="users_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def extend_presets(user_uuid: str) -> InlineKeyboardMarkup:
    """Subscription extension presets"""
    keyboard = [
        [
            InlineKeyboardButton("7 дней", callback_data=f"extend:{user_uuid}:7"),
            InlineKeyboardButton("14 дней", callback_data=f"extend:{user_uuid}:14"),
        ],
        [
            InlineKeyboardButton("30 дней", callback_data=f"extend:{user_uuid}:30"),
            InlineKeyboardButton("60 дней", callback_data=f"extend:{user_uuid}:60"),
        ],
        [
            InlineKeyboardButton("90 дней", callback_data=f"extend:{user_uuid}:90"),
            InlineKeyboardButton("180 дней", callback_data=f"extend:{user_uuid}:180"),
        ],
        [
            InlineKeyboardButton("365 дней", callback_data=f"extend:{user_uuid}:365"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data=f"user_view:{user_uuid}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def delete_confirmation(user_uuid: str) -> InlineKeyboardMarkup:
    """Delete confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"user_delete_pin:{user_uuid}"),
            InlineKeyboardButton("❌ Отмена", callback_data=f"user_view:{user_uuid}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def user_devices_actions(user_uuid: str, has_devices: bool = False) -> InlineKeyboardMarkup:
    """User devices action buttons"""
    keyboard = []
    
    if has_devices:
        keyboard.append([
            InlineKeyboardButton("🗑️ Очистить устройства", callback_data=f"user_clear_devices_confirm:{user_uuid}"),
        ])
    
    keyboard.append([
        InlineKeyboardButton("◀️ Назад к пользователю", callback_data=f"user_view:{user_uuid}"),
    ])
    
    return InlineKeyboardMarkup(keyboard)


def clear_devices_confirmation(user_uuid: str, devices_count: int) -> InlineKeyboardMarkup:
    """Clear devices confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(f"✅ Да, удалить ({devices_count} шт.)", callback_data=f"user_clear_devices_execute:{user_uuid}"),
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data=f"user_devices:{user_uuid}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def pagination(current_page: int, total_pages: int, prefix: str = "users_page") -> List[InlineKeyboardButton]:
    """Create pagination buttons"""
    buttons = []
    
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"{prefix}:{current_page-1}"))
    
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"{prefix}:{current_page+1}"))
    
    return buttons


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu button"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)


def back_to_users() -> InlineKeyboardMarkup:
    """Back to users menu button"""
    keyboard = [[InlineKeyboardButton("◀️ Меню пользователей", callback_data="users_menu")]]
    return InlineKeyboardMarkup(keyboard)
