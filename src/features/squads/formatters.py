"""
Squad data formatters
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


def format_squad_full(squad: Dict[str, Any]) -> str:
    """Format full squad information"""
    name = squad.get('name', 'N/A')
    description = squad.get('description')
    
    text_lines = [
        "👥 <b>Информация об отряде</b>",
        "",
        f"<b>Название:</b> {name}",
    ]
    
    if description:
        text_lines.append(f"<b>Описание:</b> {description}")
    
    text_lines.append("")
    text_lines.append("<b>Управление:</b>")
    text_lines.append("├ ➕ Добавить пользователей в отряд")
    text_lines.append("├ ➖ Удалить пользователей из отряда")
    text_lines.append("└ 📡 Просмотреть доступные ноды")
    
    return '\n'.join(text_lines)


def format_squad_short(squad: Dict[str, Any]) -> str:
    """Format squad in short format"""
    name = squad.get('name', 'N/A')
    info = squad.get('info', {})
    members_count = info.get('membersCount', 0) if info else 0
    
    return f"👥 <b>{name}</b> | {members_count} чел."
