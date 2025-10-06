# GitHub Actions Setup Guide

## Настройка автоматической сборки Docker образов

Для автоматической сборки и публикации Docker образов в Docker Hub при каждом push необходимо настроить GitHub Secrets.

## Шаг 1: Создание Docker Hub Access Token

1. Войдите в свой аккаунт на [Docker Hub](https://hub.docker.com/)
2. Перейдите в `Account Settings` → `Security`
3. Нажмите `New Access Token`
4. Введите название токена (например, "GitHub Actions remnabot")
5. Выберите права доступа: `Read, Write, Delete`
6. Нажмите `Generate` и **скопируйте токен** (он больше не будет показан!)

## Шаг 2: Добавление Secrets в GitHub

1. Откройте репозиторий на GitHub
2. Перейдите в `Settings` → `Secrets and variables` → `Actions`
3. Нажмите `New repository secret`
4. Создайте два секрета:

### DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: ваш username в Docker Hub (например: `dignezzz`)

### DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: токен, который вы создали на шаге 1

## Шаг 3: Проверка работы

После добавления секретов:

1. Сделайте commit и push в ветку `main`:
```bash
git add .
git commit -m "Setup Docker CI/CD"
git push origin main
```

2. Перейдите во вкладку `Actions` в вашем репозитории
3. Вы увидите запущенный workflow "Docker Build and Push"
4. Дождитесь завершения (обычно 5-10 минут)
5. Проверьте Docker Hub - новый образ должен появиться по адресу: `dignezzz/remnabot:latest`

## Автоматические теги

Workflow автоматически создаёт следующие теги:

- `latest` - последняя сборка из ветки `main`
- `develop` - последняя сборка из ветки `develop`
- `v1.0.0` - при создании git tag `v1.0.0`
- `main-abc1234` - с хешем коммита

## Создание релиза

Для создания версионного релиза:

```bash
# Создайте git tag
git tag v1.0.0
git push origin v1.0.0
```

Это запустит сборку и создаст образы:
- `dignezzz/remnabot:v1.0.0`
- `dignezzz/remnabot:1.0`
- `dignezzz/remnabot:1`
- `dignezzz/remnabot:latest`

## Multi-arch сборка

Workflow автоматически собирает образы для двух архитектур:
- `linux/amd64` (x86_64) - для большинства серверов
- `linux/arm64` (aarch64) - для ARM серверов (Raspberry Pi, Oracle ARM, и т.д.)

## Кэширование

Workflow использует GitHub Actions Cache для ускорения сборки:
- Первая сборка: ~10-15 минут
- Последующие сборки: ~3-5 минут

## Troubleshooting

### Ошибка "unauthorized: authentication required"
- Проверьте правильность `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN`
- Убедитесь, что токен имеет права `Read, Write, Delete`
- Пересоздайте токен на Docker Hub

### Ошибка "resource not accessible by integration"
- Убедитесь, что в Settings → Actions → General включено:
  - `Read and write permissions` для Workflow permissions

### Образ не появляется в Docker Hub
- Проверьте логи workflow в GitHub Actions
- Убедитесь, что push произошёл в ветку `main` или `develop`
- Проверьте, что workflow завершился успешно (зелёная галочка)

## Дополнительные настройки

### Отключение автоматической сборки

Если нужно временно отключить автоматическую сборку:

1. Отредактируйте `.github/workflows/docker-build.yml`
2. Закомментируйте строки в секции `on:` для веток, которые не нужно собирать
3. Или удалите workflow файл полностью

### Ручной запуск сборки

Workflow поддерживает ручной запуск:

1. Перейдите в `Actions` → `Docker Build and Push`
2. Нажмите `Run workflow`
3. Выберите ветку и нажмите `Run workflow`
