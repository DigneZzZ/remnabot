"""
HWID data formatters
"""
from typing import Dict, Any
from datetime import datetime


def format_date(date_str: str) -> str:
    """Format ISO date to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return date_str


def format_device_full(device: Dict[str, Any]) -> str:
    """Format full device information"""
    hwid = device.get('hwid', 'N/A')
    user_uuid = device.get('userUuid', 'N/A')
    username = device.get('username', 'N/A')
    created_at = format_date(device.get('createdAt', 'N/A'))
    last_seen = format_date(device.get('lastSeen', 'N/A'))
    
    text = f"""
📱 <b>Информация об устройстве</b>

<b>HWID:</b> <code>{hwid}</code>
<b>Пользователь:</b> {username}
<b>User UUID:</b> <code>{user_uuid}</code>

📅 <b>Даты:</b>
├ Создано: {created_at}
└ Последний вход: {last_seen}

📊 <b>Статистика:</b>
├ Всего подключений: {device.get('connectionsCount', 0)}
└ IP-адрес: {device.get('ipAddress', 'N/A')}
    """
    
    return text.strip()


def format_device_short(device: Dict[str, Any]) -> str:
    """Format device in short format"""
    hwid = device.get('hwid', 'N/A')
    username = device.get('username', 'N/A')
    
    # Truncate HWID for display
    short_hwid = hwid[:16] + '...' if len(hwid) > 16 else hwid
    
    return f"📱 <b>{username}</b> | <code>{short_hwid}</code>"
