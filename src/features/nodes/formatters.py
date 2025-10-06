"""
Node data formatters
"""
from typing import Dict, Any


def format_node_full(node: Dict[str, Any]) -> str:
    """Format full node information"""
    name = node.get('name', 'N/A')
    uuid = node.get('uuid', 'N/A')
    address = node.get('address', 'N/A')
    port = node.get('port', 'N/A')
    is_disabled = node.get('isDisabled', False)
    
    status_emoji = '🔴' if is_disabled else '🟢'
    status_text = 'Отключена' if is_disabled else 'Активна'
    
    text = f"""
📡 <b>Информация о ноде</b>

<b>Название:</b> {name}
<b>Статус:</b> {status_emoji} {status_text}
<b>UUID:</b> <code>{uuid}</code>

🌐 <b>Подключение:</b>
├ Адрес: <code>{address}</code>
└ Порт: {port}

📝 <b>Дополнительно:</b>
├ Traffic: {node.get('trafficLimitReset', 'N/A')}
└ Allow Insecure: {node.get('allowInsecure', False)}
    """
    
    return text.strip()


def format_node_short(node: Dict[str, Any]) -> str:
    """Format node in short format"""
    name = node.get('name', 'N/A')
    address = node.get('address', 'N/A')
    port = node.get('port', 'N/A')
    is_disabled = node.get('isDisabled', False)
    
    status_emoji = '🔴' if is_disabled else '🟢'
    
    return f"{status_emoji} <b>{name}</b> | {address}:{port}"
