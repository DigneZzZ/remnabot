.PHONY: help install install-dev run run-dev docker-build docker-up docker-down docker-logs clean test lint format

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make run          - Run bot locally"
	@echo "  make run-dev      - Run bot in debug mode"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start bot in Docker"
	@echo "  make docker-down  - Stop bot in Docker"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache and temp files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python -m src.main

run-dev:
	DEBUG=True LOG_LEVEL=DEBUG python -m src.main

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f remnabot

docker-dev:
	docker-compose -f docker-compose.dev.yml up

test:
	pytest tests/ -v

lint:
	flake8 src/
	mypy src/
	pylint src/

format:
	black src/
	isort src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
