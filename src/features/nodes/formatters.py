"""
Node data formatters
"""
from typing import Dict, Any


def _create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a visual progress bar using Unicode blocks"""
    if percentage < 0:
        percentage = 0
    elif percentage > 100:
        percentage = 100
    
    filled = int(length * percentage / 100)
    empty = length - filled
    
    # Используем Unicode блоки для красивого отображения
    bar = '█' * filled + '░' * empty
    
    # Добавляем цветовой индикатор через emoji
    if percentage < 50:
        indicator = '🟢'
    elif percentage < 80:
        indicator = '🟡'
    else:
        indicator = '🔴'
    
    return f"{indicator} [{bar}] {percentage:.1f}%"


def format_node_full(node: Dict[str, Any]) -> str:
    """Format full node information"""
    name = node.get('name', 'N/A')
    address = node.get('address', 'N/A')
    port = node.get('port', 'N/A')
    is_disabled = node.get('isDisabled', False)
    
    status_emoji = '🔴' if is_disabled else '🟢'
    status_text = 'Отключена' if is_disabled else 'Активна'
    
    # Формируем текст
    text_lines = [
        "📡 <b>Информация о ноде</b>",
        "",
        f"<b>Название:</b> {name}",
        f"<b>Статус:</b> {status_emoji} {status_text}",
        "",
        "🌐 <b>Подключение:</b>",
        f"├ Адрес: <code>{address}</code>",
        f"└ Порт: {port}",
    ]
    
    # Статистика трафика - показываем ВСЕГДА
    traffic_used = node.get('trafficUsedBytes', 0)
    traffic_limit = node.get('trafficLimitBytes', 0)
    is_traffic_tracking = node.get('isTrafficTrackingActive', False)
    
    # Конвертация в GB
    used_gb = traffic_used / (1024**3) if traffic_used else 0
    limit_gb = traffic_limit / (1024**3) if traffic_limit else 0
    
    text_lines.append("")
    text_lines.append("📊 <b>Трафик:</b>")
    
    if is_traffic_tracking and traffic_limit and traffic_limit > 0:
        # Если отслеживание включено и есть лимит
        percentage = (traffic_used / traffic_limit * 100) if traffic_limit > 0 else 0
        progress_bar = _create_progress_bar(percentage)
        
        text_lines.append(f"├ {progress_bar}")
        text_lines.append(f"├ Использовано: <b>{used_gb:.2f} GB</b> / {limit_gb:.2f} GB")
        
        # День сброса трафика
        reset_day = node.get('trafficResetDay')
        if reset_day:
            text_lines.append(f"└ Сброс: {reset_day}-го числа месяца")
        else:
            text_lines[-1] = text_lines[-1].replace('├', '└')
    elif is_traffic_tracking:
        # Отслеживание включено, но без лимита
        text_lines.append(f"├ Использовано: <b>{used_gb:.2f} GB</b> / ∞")
        text_lines.append(f"└ Отслеживание: <b>Включено</b>")
    else:
        # Отслеживание выключено, но показываем потребление
        text_lines.append(f"├ Использовано: <b>{used_gb:.2f} GB</b>")
        text_lines.append(f"└ Отслеживание: <b>Выключено</b>")
    
    # Коэффициент потребления (показываем только если != 1.0)
    consumption_mult = node.get('consumptionMultiplier', 1.0)
    if consumption_mult and consumption_mult != 1.0:
        text_lines.append("")
        text_lines.append(f"⚙️ <b>Коэффициент потребления:</b> {consumption_mult}x")
    
    return '\n'.join(text_lines)


def format_node_short(node: Dict[str, Any]) -> str:
    """Format node in short format"""
    name = node.get('name', 'N/A')
    address = node.get('address', 'N/A')
    port = node.get('port', 'N/A')
    is_disabled = node.get('isDisabled', False)
    
    status_emoji = '🔴' if is_disabled else '🟢'
    
    return f"{status_emoji} <b>{name}</b> | {address}:{port}"
