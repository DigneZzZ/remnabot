"""
Mass operations keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def mass_menu() -> InlineKeyboardMarkup:
    """Mass operations menu"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Активировать всех", callback_data="mass_activate"),
        ],
        [
            InlineKeyboardButton("⏸️ Деактивировать всех", callback_data="mass_deactivate"),
        ],
        [
            InlineKeyboardButton("⏰ Продлить всем", callback_data="mass_extend"),
        ],
        [
            InlineKeyboardButton("🔄 Сбросить трафик всем", callback_data="mass_reset_traffic"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def extend_days_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with preset days for mass extend"""
    keyboard = [
        [
            InlineKeyboardButton("7 дней", callback_data="mass_extend_days:7"),
            InlineKeyboardButton("14 дней", callback_data="mass_extend_days:14"),
        ],
        [
            InlineKeyboardButton("30 дней", callback_data="mass_extend_days:30"),
            InlineKeyboardButton("60 дней", callback_data="mass_extend_days:60"),
        ],
        [
            InlineKeyboardButton("90 дней", callback_data="mass_extend_days:90"),
            InlineKeyboardButton("180 дней", callback_data="mass_extend_days:180"),
        ],
        [
            InlineKeyboardButton("365 дней", callback_data="mass_extend_days:365"),
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="mass_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirmation_keyboard(operation: str) -> InlineKeyboardMarkup:
    """Confirmation keyboard for mass operations"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, выполнить", callback_data=f"mass_confirm:{operation}"),
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="mass_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main() -> InlineKeyboardMarkup:
    """Back to main menu"""
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
