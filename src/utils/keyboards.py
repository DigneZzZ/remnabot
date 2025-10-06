"""
Keyboard utilities for Telegram bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List


class Keyboards:
    """Keyboard builder for Telegram bot"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="system_stats"),
                InlineKeyboardButton("👥 Пользователи", callback_data="users_menu"),
            ],
            [
                InlineKeyboardButton("🖥️ Хосты", callback_data="hosts_menu"),
                InlineKeyboardButton("📡 Ноды", callback_data="nodes_menu"),
            ],
            [
                InlineKeyboardButton("📱 HWID", callback_data="hwid_menu"),
                InlineKeyboardButton("� Отряды", callback_data="squads_menu"),
            ],
            [
                InlineKeyboardButton("🔄 Массовые операции", callback_data="mass_menu"),
            ],
            [
                InlineKeyboardButton("⚙️ Система", callback_data="system_menu"),
                InlineKeyboardButton("🔄 Обновить", callback_data="refresh_main"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Back to main menu button"""
        keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def users_menu() -> InlineKeyboardMarkup:
        """Users management menu"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Список пользователей", callback_data="users_list"),
            ],
            [
                InlineKeyboardButton("➕ Создать пользователя", callback_data="user_create"),
            ],
            [
                InlineKeyboardButton("🔍 Поиск пользователя", callback_data="user_search"),
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_actions(user_uuid: str) -> InlineKeyboardMarkup:
        """User action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Редактировать", callback_data=f"user_edit:{user_uuid}"),
                InlineKeyboardButton("📅 Продлить", callback_data=f"user_extend:{user_uuid}"),
            ],
            [
                InlineKeyboardButton("📱 Устройства", callback_data=f"user_devices:{user_uuid}"),
            ],
            [
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"user_delete_confirm:{user_uuid}"),
            ],
            [
                InlineKeyboardButton("◀️ К списку", callback_data="users_list"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
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
    
    @staticmethod
    def confirm_delete(user_uuid: str) -> InlineKeyboardMarkup:
        """Confirm deletion with PIN"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить (введите PIN)", callback_data=f"user_delete_pin:{user_uuid}"),
            ],
            [
                InlineKeyboardButton("❌ Отмена", callback_data=f"user_view:{user_uuid}"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
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
    
    @staticmethod
    def host_actions(host_uuid: str) -> InlineKeyboardMarkup:
        """Host action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Редактировать", callback_data=f"host_edit:{host_uuid}"),
            ],
            [
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"host_delete:{host_uuid}"),
            ],
            [
                InlineKeyboardButton("◀️ К списку", callback_data="hosts_list"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
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
    
    @staticmethod
    def node_actions(node_uuid: str) -> InlineKeyboardMarkup:
        """Node action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data=f"node_stats:{node_uuid}"),
            ],
            [
                InlineKeyboardButton("✏️ Редактировать", callback_data=f"node_edit:{node_uuid}"),
            ],
            [
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"node_delete:{node_uuid}"),
            ],
            [
                InlineKeyboardButton("◀️ К списку", callback_data="nodes_list"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def hwid_menu() -> InlineKeyboardMarkup:
        """HWID management menu"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Общая статистика", callback_data="hwid_stats"),
            ],
            [
                InlineKeyboardButton("👥 Топ пользователей", callback_data="hwid_top_users"),
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def squads_menu() -> InlineKeyboardMarkup:
        """Squads management menu"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Список сквадов", callback_data="squads_list"),
            ],
            [
                InlineKeyboardButton("➕ Создать сквад", callback_data="squad_create"),
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def squad_actions(squad_uuid: str) -> InlineKeyboardMarkup:
        """Squad action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("👥 Участники", callback_data=f"squad_members:{squad_uuid}"),
            ],
            [
                InlineKeyboardButton("➕ Добавить участника", callback_data=f"squad_add_user:{squad_uuid}"),
            ],
            [
                InlineKeyboardButton("✏️ Редактировать", callback_data=f"squad_edit:{squad_uuid}"),
            ],
            [
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"squad_delete:{squad_uuid}"),
            ],
            [
                InlineKeyboardButton("◀️ К списку", callback_data="squads_list"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def mass_operations_menu() -> InlineKeyboardMarkup:
        """Mass operations menu"""
        keyboard = [
            [
                InlineKeyboardButton("📅 Массовое продление", callback_data="mass_extend"),
            ],
            [
                InlineKeyboardButton("🔄 Массовое обновление", callback_data="mass_update"),
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(
        current_page: int,
        total_pages: int,
        callback_prefix: str
    ) -> List[InlineKeyboardButton]:
        """
        Create pagination buttons
        
        Args:
            current_page: Current page number (1-indexed)
            total_pages: Total number of pages
            callback_prefix: Prefix for callback data (e.g., "users_page")
            
        Returns:
            List of pagination buttons
        """
        buttons = []
        
        if current_page > 1:
            buttons.append(
                InlineKeyboardButton("◀️ Назад", callback_data=f"{callback_prefix}:{current_page - 1}")
            )
        
        buttons.append(
            InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
        )
        
        if current_page < total_pages:
            buttons.append(
                InlineKeyboardButton("Вперед ▶️", callback_data=f"{callback_prefix}:{current_page + 1}")
            )
        
        return buttons


# Create global keyboards instance
keyboards = Keyboards()
