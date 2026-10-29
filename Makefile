# Interio — единая точка входа для сборки и проверок.

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

PYTHON ?= python3
PORT   ?= 8000
BASE_URL ?= http://localhost:$(PORT)

.PHONY: help doctor install test lint run smoke-test docs-check verify clean

help: ## Список целей
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

doctor: ## Проверить инструменты, конфигурацию и секреты (ничего не меняет)
	@./scripts/doctor.sh

install: ## Установить закреплённые зависимости
	$(PYTHON) -m pip install -r requirements-dev.txt

test: ## Тесты (аутентификация, квиз, безопасность)
	$(PYTHON) -m pytest -q

lint: ## ruff
	$(PYTHON) -m ruff check server.py tests

run: ## Запустить приложение
	$(PYTHON) server.py

smoke-test: ## Проверить живой инстанс
	@./scripts/smoke-test.sh $(BASE_URL)

docs-check: ## Проверить документацию и спецификации модулей
	@./scripts/docs-check.sh

verify: lint test docs-check ## Локальная матрица
	@echo "verify: ok"

clean: ## Удалить артефакты
	rm -rf .pytest_cache htmlcov .coverage data.db
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
