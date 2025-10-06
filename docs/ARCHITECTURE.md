# Архитектура проекта

## Обзор

Проект использует **Feature-Based Architecture** (архитектура на основе функций), где каждая функциональность выделена в отдельный модуль с чёткими границами ответственности.

## Структура проекта

```
remnabot/
├── src/
│   ├── core/               # Ядро приложения
│   │   ├── config.py       # Конфигурация
│   │   ├── bot.py          # Создание бота
│   │   └── logger.py       # Логирование
│   │
│   ├── features/           # Модули функциональности
│   │   ├── users/          # Управление пользователями
│   │   │   ├── __init__.py
│   │   │   ├── handlers.py    # Обработчики callback
│   │   │   ├── keyboards.py   # Клавиатуры
│   │   │   └── formatters.py  # Форматирование данных
│   │   │
│   │   ├── hosts/          # Управление хостами
│   │   ├── nodes/          # Управление нодами
│   │   ├── hwid/           # Управление устройствами
│   │   ├── squads/         # Управление отрядами
│   │   ├── mass_operations/# Массовые операции
│   │   └── system/         # Системные функции
│   │
│   ├── services/           # Сервисы
│   │   ├── api.py          # API клиент (обёртка SDK)
│   │   └── cache.py        # Кэширование
│   │
│   ├── middleware/         # Middleware
│   │   └── auth.py         # Аутентификация
│   │
│   ├── handlers/           # Общие handlers (deprecated)
│   │   └── start.py        # Команда /start
│   │
│   ├── utils/              # Утилиты
│   │   ├── keyboards.py    # Общие клавиатуры
│   │   └── formatters.py   # Общие форматтеры
│   │
│   └── main.py             # Точка входа
│
├── requirements.txt
├── .env.example
└── README.md
```

## Принципы архитектуры

### 1. Feature-Based Organization

Каждая feature (функция) — это самодостаточный модуль, содержащий:

- **handlers.py** — обработчики callback queries
- **keyboards.py** — построители клавиатур для UI
- **formatters.py** — форматирование данных для отображения

**Преимущества:**
- ✅ Легко найти весь код, относящийся к конкретной функции
- ✅ Можно разрабатывать функции независимо
- ✅ Легко добавлять новые функции без изменения существующего кода
- ✅ Идеально для командной разработки

### 2. Separation of Concerns (Разделение ответственности)

Каждый файл имеет чёткую ответственность:

```
handlers.py     → Логика обработки callback queries
keyboards.py    → Построение UI (клавиатур)
formatters.py   → Форматирование данных для отображения
```

**Пример:**

```python
# features/users/handlers.py
async def user_view_callback(update, context):
    # 1. Получить данные
    user = await api_client.get_user(uuid)
    
    # 2. Форматировать данные
    text = user_fmt.format_user_full(user)
    
    # 3. Показать с клавиатурой
    await query.edit_message_text(
        text,
        reply_markup=user_kb.user_actions(uuid)
    )
```

### 3. Single Responsibility Principle (SRP)

Каждый модуль отвечает только за одну функцию:

- `users/` — только управление пользователями
- `hosts/` — только управление хостами
- `nodes/` — только управление нодами
- и т.д.

### 4. Dependency Injection

Зависимости передаются через импорты:

```python
# features/users/handlers.py
from src.services.api import api_client        # API клиент
from src.middleware.auth import admin_only     # Авторизация
from . import keyboards as user_kb             # Локальные клавиатуры
from . import formatters as user_fmt           # Локальные форматтеры
```

## Регистрация handlers

Каждый feature модуль экспортирует функцию регистрации:

```python
# features/users/__init__.py
from .handlers import register_users_handlers

__all__ = ['register_users_handlers']
```

В `main.py` регистрируются все модули:

```python
# main.py
from src.features.users import register_users_handlers
from src.features.hosts import register_hosts_handlers
# ...

def main():
    application = create_bot_application()
    
    # Register feature handlers
    register_users_handlers(application)
    register_hosts_handlers(application)
    # ...
```

## Добавление новой feature

1. **Создать директорию:**

```bash
mkdir src/features/new_feature
```

2. **Создать файлы:**

```python
# __init__.py
from .handlers import register_new_feature_handlers
__all__ = ['register_new_feature_handlers']

# keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def feature_menu() -> InlineKeyboardMarkup:
    keyboard = [...]
    return InlineKeyboardMarkup(keyboard)

# formatters.py
def format_item(item: dict) -> str:
    return f"<b>{item['name']}</b>"

# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

async def feature_callback(update, context):
    # Логика
    pass

def register_new_feature_handlers(application):
    application.add_handler(CallbackQueryHandler(
        feature_callback,
        pattern="^feature_"
    ))
```

3. **Зарегистрировать в main.py:**

```python
from src.features.new_feature import register_new_feature_handlers

# В функции main():
register_new_feature_handlers(application)
```

## Интерактивный UI

Все списки теперь используют **интерактивные кнопки** вместо текста:

**До (текстовый список):**
```
Пользователи:
1. john_doe | 100MB
2. jane_doe | 50MB
```

**После (кнопки):**
```
Список пользователей

[✅ john_doe | 100MB]    ← кнопка
[✅ jane_doe | 50MB]     ← кнопка
```

**Реализация:**

```python
# features/users/handlers.py
async def users_list_callback(update, context):
    users = await api_client.get_users()
    
    keyboard = []
    for user in users:
        button_text = f"✅ {user['username']} | {format_bytes(user['traffic'])}"
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"user_view:{user['uuid']}"
            )
        ])
    
    await query.edit_message_text(
        "Выберите пользователя:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

## Паттерны callback_data

Используется структурированный формат:

```
{feature}_{action}:{param1}:{param2}
```

**Примеры:**
- `users_menu` — меню пользователей
- `users_list` — список пользователей
- `user_view:uuid-123` — просмотр пользователя
- `user_extend:uuid-123:30` — продление на 30 дней
- `host_delete:uuid-456` — удаление хоста

## Обработка ошибок

Все handlers используют единый подход:

```python
async def some_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    try:
        # Показать загрузку
        await query.edit_message_text("⏳ Загрузка...")
        
        # Выполнить операцию
        result = await api_client.some_method()
        
        # Показать результат
        await query.edit_message_text(
            format_result(result),
            reply_markup=keyboard()
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"API error: {e}")
        await query.edit_message_text(
            f"❌ Ошибка: {e}",
            reply_markup=back_button()
        )
    except Exception as e:
        log.exception("Unexpected error")
        await query.edit_message_text(
            "❌ Произошла ошибка",
            reply_markup=back_button()
        )
```

## Тестирование

Модульная структура упрощает тестирование:

```python
# tests/features/users/test_formatters.py
from src.features.users.formatters import format_user_full

def test_format_user_full():
    user = {'username': 'test', 'traffic': 1024}
    result = format_user_full(user)
    assert 'test' in result
    assert '1.00 KB' in result
```

## Миграция со старой структуры

### Старая структура (monolithic):
```
handlers/
├── users.py     (350 строк - все в одном файле)
├── hosts.py     (300 строк)
└── nodes.py     (280 строк)
```

### Новая структура (modular):
```
features/
├── users/
│   ├── handlers.py    (обработчики)
│   ├── keyboards.py   (UI)
│   └── formatters.py  (форматирование)
├── hosts/
│   ├── handlers.py
│   ├── keyboards.py
│   └── formatters.py
└── nodes/
    ├── handlers.py
    ├── keyboards.py
    └── formatters.py
```

**Преимущества:**
- Каждый файл < 200 строк (легче читать)
- Чёткое разделение ответственности
- Легко тестировать отдельные компоненты
- Легко переиспользовать код

## Best Practices

### ✅ DO:

1. **Держите feature модули независимыми**
2. **Используйте type hints**
3. **Документируйте функции docstrings**
4. **Логируйте важные операции**
5. **Обрабатывайте все исключения**
6. **Используйте константы для callback patterns**

### ❌ DON'T:

1. **Не создавайте зависимости между features**
2. **Не смешивайте логику UI и бизнес-логику**
3. **Не дублируйте код между features**
4. **Не используйте глобальное состояние**

## Производительность

- **SDK**: Использует официальный `remnawave==2.1.17`
- **Кэширование**: Redis для часто запрашиваемых данных
- **Async**: Все операции асинхронные
- **Connection pooling**: httpx в SDK использует пул соединений

## Безопасность

- **Аутентификация**: Middleware проверяет admin_id
- **Валидация**: Pydantic для валидации данных
- **Секреты**: Все токены в `.env` файле
- **Логирование**: Не логируем чувствительные данные

## Заключение

Feature-Based Architecture делает код:

- ✅ **Модульным** — каждая feature независима
- ✅ **Масштабируемым** — легко добавлять новые features
- ✅ **Поддерживаемым** — легко находить и изменять код
- ✅ **Тестируемым** — можно тестировать каждую feature отдельно
- ✅ **Читаемым** — чёткая структура и разделение

Это современный подход, используемый в крупных проектах и командной разработке.
