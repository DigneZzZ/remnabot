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
    uuid = squad.get('uuid', 'N/A')
    description = squad.get('description', 'Описание отсутствует')
    members_count = squad.get('membersCount', 0)
    created_at = format_date(squad.get('createdAt', 'N/A'))
    
    text = f"""
👥 <b>Информация об отряде</b>

<b>Название:</b> {name}
<b>UUID:</b> <code>{uuid}</code>
<b>Описание:</b> {description}

👤 <b>Участники:</b> {members_count} чел.

📅 <b>Создан:</b> {created_at}
    """
    
    return text.strip()


def format_squad_short(squad: Dict[str, Any]) -> str:
    """Format squad in short format"""
    name = squad.get('name', 'N/A')
    members_count = squad.get('membersCount', 0)
    
    return f"👥 <b>{name}</b> | {members_count} чел."
