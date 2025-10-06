"""
Host data formatters
"""
from typing import Dict, Any


def format_host_full(host: Dict[str, Any]) -> str:
    """Format full host information"""
    remark = host.get('remark', 'N/A')
    uuid = host.get('uuid', 'N/A')
    address = host.get('address', 'N/A')
    port = host.get('port', 'N/A')
    is_disabled = host.get('isDisabled', False)
    security_layer = host.get('securityLayer', 'N/A')
    
    status_emoji = '🔴' if is_disabled else '🟢'
    status_text = 'Отключен' if is_disabled else 'Активен'
    
    text = f"""
🖥️ <b>Информация о хосте</b>

<b>Название:</b> {remark}
<b>Статус:</b> {status_emoji} {status_text}
<b>UUID:</b> <code>{uuid}</code>

📡 <b>Подключение:</b>
├ Адрес: <code>{address}</code>
├ Порт: {port}
└ Безопасность: {security_layer}

📝 <b>Дополнительно:</b>
├ SNI: {host.get('sni', 'Не указан')}
├ Host: {host.get('host', 'Не указан')}
├ Path: {host.get('path', 'Не указан')}
└ ALPN: {host.get('alpn', 'Не указан')}
    """
    
    return text.strip()


def format_host_short(host: Dict[str, Any]) -> str:
    """Format host in short format"""
    remark = host.get('remark', 'N/A')
    address = host.get('address', 'N/A')
    port = host.get('port', 'N/A')
    is_disabled = host.get('isDisabled', False)
    
    status_emoji = '🔴' if is_disabled else '🟢'
    
    return f"{status_emoji} <b>{remark}</b> | {address}:{port}"
