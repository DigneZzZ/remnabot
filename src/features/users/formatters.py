"""
User data formatters
"""
from typing import Dict, Any
from datetime import datetime


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    value = float(bytes_value)
    
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    
    return f"{value:.2f} {units[unit_index]}"


def format_date(date_str: str) -> str:
    """Format ISO date to readable format"""
    if not date_str:
        return "N/A"
    
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime("%d.%m.%Y %H:%M")
    except:
        return date_str


def format_user_full(user: Dict[str, Any]) -> str:
    """Format full user information"""
    username = user.get('username', 'N/A')
    uuid = user.get('uuid', 'N/A')
    short_uuid = user.get('shortUuid', 'N/A')
    status = user.get('status', 'unknown').upper()
    
    # Traffic info
    used_traffic = format_bytes(user.get('usedTrafficBytes', 0))
    lifetime_traffic = format_bytes(user.get('lifetimeUsedTrafficBytes', 0))
    traffic_limit = user.get('trafficLimitBytes', 0)
    traffic_limit_str = format_bytes(traffic_limit) if traffic_limit else "∞"
    
    # Dates
    created_at = format_date(user.get('createdAt', ''))
    expire_at = format_date(user.get('expireAt', ''))
    online_at = format_date(user.get('onlineAt', '')) if user.get('onlineAt') else "Никогда"
    
    # Status emoji
    status_emoji = {
        'ACTIVE': '✅',
        'DISABLED': '🚫',
        'LIMITED': '⚠️',
        'EXPIRED': '⏱️'
    }.get(status, '❓')
    
    # Additional info
    email = user.get('email', 'Не указан')
    telegram_id = user.get('telegramId', 'Не указан')
    description = user.get('description', 'Нет описания')
    
    text = f"""
👤 <b>Информация о пользователе</b>

<b>Имя:</b> {username}
<b>Статус:</b> {status_emoji} {status}
<b>UUID:</b> <code>{uuid}</code>
<b>Short UUID:</b> <code>{short_uuid}</code>

📊 <b>Трафик:</b>
├ Использовано: {used_traffic}
├ Всего за время: {lifetime_traffic}
└ Лимит: {traffic_limit_str}

📅 <b>Даты:</b>
├ Создан: {created_at}
├ Истекает: {expire_at}
└ Последний вход: {online_at}

📝 <b>Дополнительно:</b>
├ Email: {email}
├ Telegram ID: {telegram_id}
└ Описание: {description}
    """
    
    return text.strip()


def format_user_short(user: Dict[str, Any]) -> str:
    """Format user in short format for lists"""
    username = user.get('username', 'N/A')
    status = user.get('status', 'unknown').upper()
    used_traffic = format_bytes(user.get('usedTrafficBytes', 0))
    
    status_emoji = {
        'ACTIVE': '✅',
        'DISABLED': '🚫',
        'LIMITED': '⚠️',
        'EXPIRED': '⏱️'
    }.get(status, '❓')
    
    return f"{status_emoji} <b>{username}</b> | {used_traffic}"


def status_badge(status: str) -> str:
    """Return status emoji badge"""
    status_emoji = {
        'ACTIVE': '✅',
        'DISABLED': '🚫',
        'LIMITED': '⚠️',
        'EXPIRED': '⏱️',
        'UNKNOWN': '❓'
    }
    return status_emoji.get(status.upper(), '❓')


def progress_bar(percent: float, width: int = 10) -> str:
    """Generate text progress bar"""
    filled = int((percent / 100) * width)
    empty = width - filled
    
    # Используем блоки для визуализации
    bar = '█' * filled + '░' * empty
    return bar
