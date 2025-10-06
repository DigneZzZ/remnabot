"""
System data formatters
"""
from typing import Dict, Any


def format_bytes(bytes_count: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_system_stats(stats: Dict[str, Any]) -> str:
    """Format system statistics"""
    total_users = stats.get('totalUsers', 0)
    active_users = stats.get('activeUsers', 0)
    total_traffic = format_bytes(stats.get('totalTraffic', 0))
    
    text = f"""
📊 <b>Статистика системы</b>

👥 <b>Пользователи:</b>
├ Всего: {total_users}
└ Активных: {active_users}

📈 <b>Трафик:</b>
└ Всего использовано: {total_traffic}

🖥️ <b>Хосты:</b> {stats.get('totalHosts', 0)}
📡 <b>Ноды:</b> {stats.get('totalNodes', 0)}
👥 <b>Отряды:</b> {stats.get('totalSquads', 0)}
📱 <b>Устройства:</b> {stats.get('totalDevices', 0)}
    """
    
    return text.strip()
