"""
Mass operations formatters
"""
from typing import Dict, Any


def format_operation_result(result: Dict[str, Any]) -> str:
    """Format mass operation result"""
    success_count = result.get('successCount', 0)
    failed_count = result.get('failedCount', 0)
    total = success_count + failed_count
    
    emoji = "✅" if failed_count == 0 else "⚠️"
    
    text = f"""
{emoji} <b>Результат массовой операции</b>

📊 <b>Статистика:</b>
├ Всего: {total}
├ Успешно: {success_count}
└ Ошибок: {failed_count}
    """
    
    if failed_count > 0:
        text += "\n\n⚠️ Некоторые операции завершились с ошибками"
    
    return text.strip()
