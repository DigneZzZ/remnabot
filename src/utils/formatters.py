"""
Formatters for displaying data in Telegram messages
"""
from typing import Dict, Any, List
from datetime import datetime
from dateutil import parser as date_parser


class Formatters:
    """Text formatting utilities"""
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Format bytes to human readable format
        
        Args:
            bytes_value: Bytes value
            
        Returns:
            Formatted string (e.g., "1.5 GB")
        """
        if bytes_value is None:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @staticmethod
    def format_date(date_string: str) -> str:
        """
        Format ISO date string to readable format
        
        Args:
            date_string: ISO date string
            
        Returns:
            Formatted date string
        """
        if not date_string:
            return "N/A"
        
        try:
            dt = date_parser.parse(date_string)
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return date_string
    
    @staticmethod
    def format_user(user_data: Dict[str, Any]) -> str:
        """
        Format user data for display
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Formatted user info
        """
        username = user_data.get('username', 'N/A')
        uuid = user_data.get('uuid', 'N/A')
        email = user_data.get('email', 'N/A')
        status = user_data.get('status', 'unknown')
        created = Formatters.format_date(user_data.get('createdAt', ''))
        expires = Formatters.format_date(user_data.get('expiresAt', ''))
        
        # Traffic info
        used_traffic = Formatters.format_bytes(user_data.get('usedTraffic', 0))
        traffic_limit = user_data.get('trafficLimit')
        traffic_limit_str = Formatters.format_bytes(traffic_limit) if traffic_limit else "∞"
        
        # Status emoji
        status_emoji = {
            'active': '✅',
            'inactive': '❌',
            'suspended': '⏸️',
            'disabled': '🚫',
            'limited': '⚠️',
            'expired': '⏱️'
        }.get(status.lower(), '❓')
        
        text = f"""
👤 <b>Пользователь</b>

<b>Имя:</b> {username}
<b>UUID:</b> <code>{uuid}</code>
<b>Email:</b> {email}
<b>Статус:</b> {status_emoji} {status}

📊 <b>Трафик:</b>
└ Использовано: {used_traffic} / {traffic_limit_str}

📅 <b>Даты:</b>
└ Создан: {created}
└ Истекает: {expires}
        """
        
        return text.strip()
    
    @staticmethod
    def format_user_short(user_data: Dict[str, Any]) -> str:
        """
        Format user data in short format for lists
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Formatted user info (short)
        """
        username = user_data.get('username', 'N/A')
        status = user_data.get('status', 'unknown')
        
        status_emoji = {
            'active': '✅',
            'inactive': '❌',
            'suspended': '⏸️',
            'disabled': '🚫',
            'limited': '⚠️',
            'expired': '⏱️'
        }.get(status.lower(), '❓')
        
        return f"{status_emoji} <b>{username}</b> ({status})"
    
    @staticmethod
    def format_host(host_data: Dict[str, Any]) -> str:
        """Format host data for display"""
        name = host_data.get('name', 'N/A')
        uuid = host_data.get('uuid', 'N/A')
        address = host_data.get('address', 'N/A')
        port = host_data.get('port', 'N/A')
        status = host_data.get('status', 'unknown')
        
        status_emoji = '✅' if status == 'online' else '❌'
        
        text = f"""
🖥️ <b>Хост</b>

<b>Название:</b> {name}
<b>UUID:</b> <code>{uuid}</code>
<b>Адрес:</b> {address}:{port}
<b>Статус:</b> {status_emoji} {status}
        """
        
        return text.strip()
    
    @staticmethod
    def format_node(node_data: Dict[str, Any]) -> str:
        """Format node data for display"""
        name = node_data.get('name', 'N/A')
        uuid = node_data.get('uuid', 'N/A')
        status = node_data.get('status', 'unknown')
        users_count = node_data.get('usersCount', 0)
        
        status_emoji = '✅' if status == 'online' else '❌'
        
        text = f"""
🌐 <b>Нода</b>

<b>Название:</b> {name}
<b>UUID:</b> <code>{uuid}</code>
<b>Статус:</b> {status_emoji} {status}
<b>Пользователей:</b> {users_count}
        """
        
        return text.strip()
    
    @staticmethod
    def format_node_stats(node_data: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Format node statistics"""
        name = node_data.get('name', 'N/A')
        
        total_traffic = Formatters.format_bytes(stats.get('totalTraffic', 0))
        upload_traffic = Formatters.format_bytes(stats.get('uploadTraffic', 0))
        download_traffic = Formatters.format_bytes(stats.get('downloadTraffic', 0))
        users_online = stats.get('usersOnline', 0)
        total_users = stats.get('totalUsers', 0)
        
        text = f"""
📊 <b>Статистика ноды: {name}</b>

<b>Трафик:</b>
└ Всего: {total_traffic}
└ Загрузка: {upload_traffic}
└ Выгрузка: {download_traffic}

<b>Пользователи:</b>
└ Онлайн: {users_online}
└ Всего: {total_users}
        """
        
        return text.strip()
    
    @staticmethod
    def format_squad(squad_data: Dict[str, Any]) -> str:
        """Format squad data for display"""
        name = squad_data.get('name', 'N/A')
        uuid = squad_data.get('uuid', 'N/A')
        description = squad_data.get('description', '')
        members_count = squad_data.get('membersCount', 0)
        
        text = f"""
👨‍👩‍👧‍👦 <b>Сквад</b>

<b>Название:</b> {name}
<b>UUID:</b> <code>{uuid}</code>
<b>Описание:</b> {description or 'Нет описания'}
<b>Участников:</b> {members_count}
        """
        
        return text.strip()
    
    @staticmethod
    def format_system_stats(stats: Dict[str, Any]) -> str:
        """Format system statistics"""
        # API returns data in 'response' field
        data = stats.get('response', stats)
        
        # Users info
        users_data = data.get('users', {})
        total_users = users_data.get('totalUsers', 0)
        status_counts = users_data.get('statusCounts', {})
        active_users = status_counts.get('ACTIVE', 0)
        disabled_users = status_counts.get('DISABLED', 0)
        expired_users = status_counts.get('EXPIRED', 0)
        
        # Traffic info
        total_traffic_bytes = int(users_data.get('totalTrafficBytes', 0))
        total_traffic = Formatters.format_bytes(total_traffic_bytes)
        
        # Online stats
        online_stats = data.get('onlineStats', {})
        online_now = online_stats.get('onlineNow', 0)
        last_day = online_stats.get('lastDay', 0)
        never_online = online_stats.get('neverOnline', 0)
        
        # Nodes
        nodes_data = data.get('nodes', {})
        nodes_online = nodes_data.get('totalOnline', 0)
        
        # System info
        memory = data.get('memory', {})
        memory_total = Formatters.format_bytes(memory.get('total', 0))
        memory_used = Formatters.format_bytes(memory.get('used', 0))
        cpu = data.get('cpu', {})
        cpu_cores = cpu.get('cores', 0)
        
        text = f"""
📊 <b>Статистика системы</b>

👥 <b>Пользователи:</b>
└ Всего: {total_users}
└ ✅ Активных: {active_users}
└ ⏸️ Отключенных: {disabled_users}
└ ⏱️ Истекших: {expired_users}

🌐 <b>Онлайн:</b>
└ Сейчас: {online_now}
└ За сутки: {last_day}
└ Никогда не были: {never_online}

📈 <b>Трафик:</b>
└ Всего использовано: {total_traffic}

🖥️ <b>Инфраструктура:</b>
└ Нод онлайн: {nodes_online}
└ CPU ядер: {cpu_cores}
└ RAM: {memory_used} / {memory_total}
        """
        
        return text.strip()
    
    @staticmethod
    def format_devices_stats(stats: Dict[str, Any]) -> str:
        """Format devices statistics"""
        total_devices = stats.get('totalDevices', 0)
        active_devices = stats.get('activeDevices', 0)
        
        text = f"""
📱 <b>Статистика устройств (HWID)</b>

<b>Всего устройств:</b> {total_devices}
<b>Активных:</b> {active_devices}
        """
        
        return text.strip()
    
    @staticmethod
    def format_top_users_by_devices(users: List[Dict[str, Any]]) -> str:
        """Format top users by device count"""
        if not users:
            return "📱 <b>Пользователи с наибольшим количеством устройств</b>\n\nНет данных"
        
        text = "📱 <b>Топ пользователей по устройствам</b>\n\n"
        
        for i, user in enumerate(users[:10], 1):
            username = user.get('username', 'N/A')
            devices_count = user.get('devicesCount', 0)
            text += f"{i}. <b>{username}</b> - {devices_count} устройств\n"
        
        return text.strip()
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape special characters for Markdown"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text


# Create global formatters instance
formatters = Formatters()
