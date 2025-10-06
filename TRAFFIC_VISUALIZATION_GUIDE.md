# Графическое представление статистики трафика в Telegram

## 🎯 Текущая реализация

### ✅ Что уже сделано:
1. **Прогресс-бар с использованием Unicode блоков**
   - Визуальное отображение: `🟢 [████████░░] 80.5%`
   - Цветовые индикаторы:
     - 🟢 Зелёный: < 50% использовано
     - 🟡 Жёлтый: 50-80% использовано
     - 🔴 Красный: > 80% использовано

2. **Всегда отображается потребление трафика**
   - Даже если отслеживание выключено
   - Показывается текущее использование в GB

## 📊 Варианты для графиков за несколько дней

### Вариант 1: ASCII-графики прямо в сообщении ⭐ РЕКОМЕНДУЕТСЯ

**Преимущества:**
- Не требует дополнительных библиотек
- Работает везде, быстро
- Простая реализация

**Пример реализации:**
```python
def create_ascii_chart(data_points: List[float], max_height: int = 5) -> str:
    """
    Создаёт ASCII график из массива данных
    data_points: список значений (GB) за последние дни
    """
    if not data_points:
        return "Нет данных"
    
    max_val = max(data_points)
    if max_val == 0:
        max_val = 1
    
    # Нормализуем значения
    normalized = [int((val / max_val) * max_height) for val in data_points]
    
    # Создаём график построчно (сверху вниз)
    lines = []
    for level in range(max_height, 0, -1):
        line = ""
        for val in normalized:
            if val >= level:
                line += "█"
            else:
                line += " "
        lines.append(line)
    
    # Добавляем ось X с датами
    labels = "".join(["▔" for _ in data_points])
    lines.append(labels)
    
    return "\n".join(lines)
```

**Вывод будет выглядеть так:**
```
📊 Трафик за последние 5 дней:
   █  █
  ██ ██
 ███ ██
 ███████
▔▔▔▔▔▔▔
1 2 3 4 5 дн
```

### Вариант 2: Unicode блоки вертикальный график

**Преимущества:**
- Компактный
- Красивый
- Не требует библиотек

**Пример:**
```python
def create_vertical_bar_chart(data_points: List[float]) -> str:
    """Создаёт вертикальный график используя Unicode блоки"""
    if not data_points:
        return "Нет данных"
    
    max_val = max(data_points) if max(data_points) > 0 else 1
    bars = []
    
    # Unicode блоки для вертикальных баров разной высоты
    blocks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    for val in data_points:
        normalized = int((val / max_val) * (len(blocks) - 1))
        bars.append(blocks[normalized])
    
    return ''.join(bars)
```

**Вывод:**
```
📊 Трафик: ▁▃▅▇█▇▅▃ (последние 7 дней)
```

### Вариант 3: Spark lines (мини-графики)

**Самый компактный вариант:**
```python
def create_sparkline(data_points: List[float]) -> str:
    """Создаёт sparkline график"""
    if not data_points:
        return "Нет данных"
    
    max_val = max(data_points) if max(data_points) > 0 else 1
    sparks = '▁▂▃▄▅▆▇█'
    
    result = []
    for val in data_points:
        index = int((val / max_val) * (len(sparks) - 1))
        result.append(sparks[index])
    
    return ''.join(result)
```

**Вывод:**
```
📈 Динамика: █▇▆▅▄▃▂▁ ↓ Снижение
```

### Вариант 4: Генерация изображения (matplotlib) 🎨

**Преимущества:**
- Профессиональный вид
- Множество возможностей кастомизации
- Легенды, оси, цвета

**Недостатки:**
- Требует matplotlib, pillow
- Медленнее
- Увеличивает размер сообщений

**Пример:**
```python
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.dates as mdates

def create_traffic_chart(dates: List[str], data: List[float]) -> BytesIO:
    """Создаёт график трафика и возвращает как BytesIO"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(dates, data, marker='o', linewidth=2, color='#00ff88')
    ax.fill_between(dates, data, alpha=0.3, color='#00ff88')
    
    ax.set_xlabel('Дата')
    ax.set_ylabel('Трафик (GB)')
    ax.set_title('Статистика трафика ноды')
    ax.grid(True, alpha=0.3)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

# Использование в хендлере:
async def show_node_stats(update, context):
    # ... получение данных ...
    chart = create_traffic_chart(dates, data)
    await update.message.reply_photo(
        photo=chart,
        caption="📊 Статистика трафика за последние 7 дней"
    )
```

### Вариант 5: Комбинированный подход ⭐⭐ ЛУЧШИЙ ВАРИАНТ

**Рекомендуется использовать оба:**
1. **ASCII/Unicode график в обычном просмотре** - быстро и всегда доступно
2. **Кнопка "📊 Детальная статистика"** - генерирует красивый график-изображение

**Пример структуры:**
```
📡 Информация о ноде

Название: 4vps
Статус: 🟢 Активна

📊 Трафик:
🟢 [████████░░] 80.5%
├ Использовано: 45.2 GB / 56.0 GB
├ Динамика: ▃▄▅▆▇▇▆ (7 дней)
└ Сброс: 1-го числа месяца

[📊 Детальная статистика]  [⚙️ Настройки]
```

## 🛠️ Рекомендации по реализации

### Для быстрого старта:
1. **Используйте Unicode блоки** (Варианты 2 и 3) - просто и красиво
2. Добавьте эмодзи-индикаторы тренда: ↑ ↓ → 

### Для полноценной реализации:
1. **Храните статистику в базе данных** (или Redis)
   - Ежедневные снимки потребления
   - История за 30 дней
   
2. **Создайте отдельный хендлер** для детальной статистики
   ```python
   @admin_only
   async def node_detailed_stats(update, context):
       # Генерирует matplotlib график
       pass
   ```

3. **Добавьте кэширование** графиков
   - Генерируйте раз в час
   - Храните в Redis или на диске

## 📝 Что нужно для реализации с историей

### Требования к API/Базе данных:
```python
# Пример структуры данных
{
    "nodeUuid": "304cb33f-8006-40ef-a849-89af07127a0a",
    "dailyStats": [
        {
            "date": "2025-10-01",
            "trafficBytes": 5368709120,  # 5 GB
            "usersOnline": 12
        },
        {
            "date": "2025-10-02",
            "trafficBytes": 7516192768,  # 7 GB
            "usersOnline": 15
        },
        # ... за последние 30 дней
    ]
}
```

### Если API не предоставляет историю:
**Вариант А: Собирайте статистику локально**
```python
# В отдельной задаче (например, через APScheduler)
async def collect_node_stats():
    """Запускается каждый день в 00:00"""
    nodes = await api_client.get_nodes()
    for node in nodes:
        stats = {
            'date': datetime.now().date(),
            'traffic': node['trafficUsedBytes'],
            'users': node.get('usersOnline', 0)
        }
        # Сохраняем в локальную БД (SQLite или Redis)
        await save_daily_stats(node['uuid'], stats)
```

**Вариант Б: Используйте метрики Prometheus/Grafana**
- Если Remnawave экспортирует метрики
- Можно запрашивать через API Prometheus

## 🎨 Примеры финального вывода

### Минималистичный:
```
📡 4vps

🟢 [████████░░] 80.5%
📊 45.2 GB / 56.0 GB
📈 ▃▄▅▆▇▇▆ (↑ +2.1 GB)
```

### Детальный:
```
📡 Информация о ноде

Название: 4vps
Статус: 🟢 Активна

🌐 Подключение:
├ Адрес: 45.129.185.179
└ Порт: 3000

📊 Трафик:
🟢 [████████░░] 80.5%
├ Использовано: 45.2 GB / 56.0 GB
├ Тренд (7 дн): ▃▄▅▆▇▇▆ ↑
├ Сегодня: +2.1 GB (↑ 4.9%)
└ Сброс: 1-го числа месяца

⚙️ Коэффициент потребления: 1.0x

[📊 Детальный график] [⚙️ Настройки]
```

## 💡 Следующие шаги

1. ✅ **Реализован базовый прогресс-бар** - ГОТОВО
2. 🔲 Добавить простой Unicode график (5 минут кода)
3. 🔲 Настроить сбор ежедневной статистики
4. 🔲 Добавить кнопку "Детальная статистика" с matplotlib
5. 🔲 Реализовать кэширование графиков

Хотите, чтобы я сейчас добавил простой Unicode график (пункт 2)?
