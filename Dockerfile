# Multi-stage build для оптимизации размера образа
FROM python:3.13-slim as builder

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
WORKDIR /app
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.13-slim

# Build arguments
ARG BUILDTIME
ARG VERSION
ARG REVISION

# Метаданные (OCI labels)
LABEL org.opencontainers.image.created="${BUILDTIME}"
LABEL org.opencontainers.image.authors="DigneZzZ"
LABEL org.opencontainers.image.url="https://github.com/DigneZzZ/remnabot"
LABEL org.opencontainers.image.documentation="https://github.com/DigneZzZ/remnabot/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/DigneZzZ/remnabot"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${REVISION}"
LABEL org.opencontainers.image.vendor="DigneZzZ"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="Remnawave Telegram Bot"
LABEL org.opencontainers.image.description="Advanced Telegram bot for Remnawave panel management with user creation, bulk operations, and comprehensive administration"

# Создаём пользователя для запуска приложения
RUN useradd -m -u 1000 botuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /home/botuser/.local

# Копируем исходный код
COPY --chown=botuser:botuser src/ ./src/

# Настраиваем PATH для пользовательских пакетов
ENV PATH=/home/botuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Переключаемся на непривилегированного пользователя
USER botuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Запуск бота
CMD ["python", "-m", "src.main"]
