# Remnawave Telegram Bot

Telegram бот для управления Remnawave панелью - системой управления прокси-серверами и пользователями.

## 🚀 Возможности

- 📊 **Статистика**: Отображение важной статистики панели
- 👥 **Управление пользователями**: Создание, редактирование, продление подписок, удаление (с подтверждением)
- � **Массовое создание пользователей**: Создание до 20 пользователей одновременно с пресетами (трафик, срок, период сброса)
- 🔍 **Поиск пользователей**: Поиск по username, UUID, email, Telegram ID с поддержкой подстрок
- �🖥️ **Управление хостами**: Полное управление хостами
- 🌐 **Управление нодами**: Управление нодами с детальной статистикой по трафику
- 📱 **Управление HWID**: Статистика устройств, выборка пользователей с наибольшим количеством устройств
- 🔄 **Массовые операции**: Массовое управление пользователями (кроме удаления)
- 👥 **Управление сквадами**: Управление группами пользователей
- 🔐 **Безопасность**: Доступ только для авторизованных администраторов
- 🐳 **Docker Ready**: Автоматическая сборка и публикация в Docker Hub

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose (для запуска в контейнере)
- Remnawave API (панель управления)
- Telegram Bot Token
- Redis (опционально, для кэширования)

## 🛠️ Установка

### Вариант 1: Запуск с Docker Hub (Production - Рекомендуется)

Образы автоматически собираются и публикуются в Docker Hub при каждом push в `main`.

1. Скачайте docker-compose.yml:

```bash
wget https://raw.githubusercontent.com/DigneZzZ/remnabot/main/docker-compose.yml
```

2. Создайте файл `.env`:

```bash
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321
REMNAWAVE_API_URL=https://your-api-url.com
REMNAWAVE_API_TOKEN=your_api_token
PIN_CODE=1234
LOG_LEVEL=INFO
DEBUG=false
REDIS_ENABLED=false
MAX_BULK_CREATE=20
EOF
```

3. Запустите контейнеры:

```bash
docker-compose up -d
```

4. Просмотр логов:

```bash
docker-compose logs -f remnabot
```

5. Остановка:

```bash
docker-compose down
```

### Вариант 2: Сборка из исходников

1. Клонируйте репозиторий:

```bash
git clone https://github.com/DigneZzZ/remnabot.git
cd remnabot
```

2. Создайте `.env` файл на основе `.env.example`:

```bash
cp .env.example .env
nano .env  # Отредактируйте переменные
```

3. Соберите и запустите:

```bash
docker build -t remnabot .
docker-compose up -d
```

### Вариант 2: Локальная разработка (Dev)

1. Создайте виртуальное окружение:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Установите зависимости:
```bash
pip install -r requirements-dev.txt
```

3. Создайте `.env` файл и настройте его

4. Запустите бота:
```bash
# С дебаг-логами
DEBUG=True LOG_LEVEL=DEBUG python -m src.main
```

### Вариант 3: Разработка в Docker

```bash
docker-compose -f docker-compose.dev.yml up
```

## 📁 Структура проекта

```
remnabot/
├── src/
│   ├── core/           # Ядро приложения
│   │   ├── config.py   # Конфигурация
│   │   ├── logger.py   # Логирование
│   │   └── bot.py      # Инициализация бота
│   ├── handlers/       # Обработчики команд
│   │   ├── start.py    # Стартовые команды
│   │   ├── users.py    # Управление пользователями
│   │   ├── hosts.py    # Управление хостами
│   │   ├── nodes.py    # Управление нодами
│   │   ├── hwid.py     # Управление HWID
│   │   ├── squads.py   # Управление сквадами
│   │   └── mass.py     # Массовые операции
│   ├── services/       # Сервисы
│   │   ├── api.py      # Remnawave API клиент
│   │   └── cache.py    # Кэширование
│   ├── middleware/     # Middleware
│   │   └── auth.py     # Проверка админов
│   ├── utils/          # Утилиты
│   │   ├── keyboards.py # Клавиатуры
│   │   ├── formatters.py # Форматирование
│   │   └── validators.py # Валидация
│   ├── models/         # Модели данных
│   │   └── schemas.py
│   └── main.py         # Точка входа
├── logs/               # Логи
├── .env.example        # Пример конфигурации
├── requirements.txt    # Зависимости
├── Dockerfile          # Docker образ
└── docker-compose.yml  # Docker Compose
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательна |
|------------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | ✅ |
| `ADMIN_IDS` | ID администраторов (через запятую) | ✅ |
| `REMNAWAVE_API_URL` | URL Remnawave API | ✅ |
| `REMNAWAVE_USERNAME` | Логин администратора | ✅ |
| `REMNAWAVE_PASSWORD` | Пароль администратора | ✅ |
| `PIN_CODE` | PIN для подтверждения удаления | ✅ |
| `LOG_LEVEL` | Уровень логирования (DEBUG/INFO/WARNING/ERROR) | ❌ |
| `DEBUG` | Режим отладки (True/False) | ❌ |
| `REDIS_URL` | URL Redis сервера | ❌ |
| `REDIS_ENABLED` | Включить Redis кэширование | ❌ |
| `MAX_BULK_CREATE` | Максимум пользователей для массового создания | ❌ |

## 🐳 Docker & CI/CD

### Docker Hub

Образы автоматически публикуются в Docker Hub при каждом push:

- **Latest (main branch)**: `dignezzz/remnabot:latest`
- **Tagged releases**: `dignezzz/remnabot:v1.0.0`
- **Branch builds**: `dignezzz/remnabot:develop`

### GitHub Actions

Репозиторий использует GitHub Actions для автоматической сборки:

- ✅ Автоматическая сборка при push в `main` и `develop`
- ✅ Multi-arch сборка (amd64, arm64)
- ✅ Кэширование слоёв для ускорения сборки
- ✅ Автоматическое создание тегов из версий
- ✅ Публикация в Docker Hub

### Настройка GitHub Secrets

Для работы CI/CD необходимо добавить в GitHub Secrets:

1. `DOCKERHUB_USERNAME` - ваш Docker Hub username
2. `DOCKERHUB_TOKEN` - Docker Hub access token

### Docker Compose профили

```bash
# Production (использует образ из Docker Hub)
docker-compose up -d

# Development (монтирует локальный код)
docker-compose -f docker-compose.dev.yml up

# С Redis
REDIS_ENABLED=true docker-compose up -d
```

## 🎯 Использование

После запуска бота отправьте команду `/start`. Бот проверит ваш Telegram ID на соответствие списку администраторов.

### Основные команды:

- `/start` - Запуск бота и отображение главного меню
- `/stats` - Общая статистика системы
- `/users` - Управление пользователями
- `/hosts` - Управление хостами
- `/nodes` - Управление нодами
- `/hwid` - Управление HWID устройствами
- `/squads` - Управление сквадами
- `/mass` - Массовые операции

## 🔐 Безопасность

- Доступ к боту имеют только пользователи с ID из списка `ADMIN_IDS`
- Удаление пользователей требует подтверждения PIN-кодом
- Все критические операции логируются
- Пароли и токены хранятся только в переменных окружения

## 📝 Логирование

В режиме DEBUG логи содержат подробную информацию о всех операциях:
- API запросы и ответы
- Действия пользователей
- Ошибки и исключения

Логи сохраняются в директории `logs/` и ротируются автоматически.

## 🤝 Разработка

### Добавление новых команд

1. Создайте новый handler в `src/handlers/`
2. Зарегистрируйте handler в `src/main.py`
3. Добавьте соответствующую клавиатуру в `src/utils/keyboards.py`

### Тестирование

```bash
pytest tests/
```

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 👤 Автор

DigneZzZ

## 🐛 Баги и предложения

Используйте [Issues](https://github.com/DigneZzZ/remnabot/issues) для сообщений о багах и предложений по улучшению.
