# Сборка и запуск

## Закреплённые версии

| Инструмент | Версия | Источник истины |
| --- | --- | --- |
| Python | 3.11+ (проверено на 3.13) | `render.yaml`, `README.md` |
| Runtime-зависимости | точные версии (`==`) | `requirements.txt` |
| Dev-зависимости | точные версии (`==`) | `requirements-dev.txt` |
| httpx | 0.27.x | иначе `TestClient` несовместим с FastAPI 0.104 |

## Уровень A — исходный код

```bash
make doctor    # инструменты, зависимости, конфигурация, отсутствие секретов в коде
make install
make lint
make test      # 15 тестов; сеть не используется
make docs-check
```

## Уровень B — запуск

```bash
cp .env.example .env     # задать ADMIN_CODE
make run                 # uvicorn на 8000
```

Отдельного артефакта сборки нет: приложение интерпретируется.

## Уровень C — проверка живого инстанса

```bash
make smoke-test BASE_URL=http://localhost:8000
```

## Уровень D — CI

`.github/workflows/ci.yml`: тесты, ruff, запуск без опциональной конфигурации
(`ADMIN_CODE` не задан → админ-вход обязан отвечать 503), проверка документации.

## Переменные окружения

| Переменная | Обязательна | Без неё |
| --- | --- | --- |
| `ADMIN_CODE` | для админ-доступа | `/api/auth/admin-login` → 503 |
| `SMTP_USERNAME`/`SMTP_PASSWORD` | нет | письма не отправляются |
| `DB_PATH` | нет | `data.db` в рабочем каталоге |
| `CORS_ORIGINS` | нет | только same-origin |
| `KEEP_ALIVE_ENABLED` | нет | keep-alive выключен |
| `ENV` | нет | `development`; `test` отключает keep-alive |

## Типовые ошибки

| Ошибка | Причина | Решение |
| --- | --- | --- |
| `Client.__init__() got an unexpected keyword argument 'app'` | httpx новее, чем поддерживает FastAPI 0.104 | `pip install httpx==0.27.2` |
| Админ-вход отвечает 503 | `ADMIN_CODE` не задан | задать в `.env` |
| Письма не приходят | SMTP не настроен | задать учётные данные (и перевыпустить старый пароль) |
| Данные исчезают после рестарта | `data.db` не на постоянном диске | подключить диск на хостинге |
| Тесты падают с 409 | общая база между тестами | `tests/conftest.py` даёт каждому тесту свою БД |

## Доказательство

`ci.yml` (тесты, lint, запуск без опций, документация) и `make smoke-test` после
развёртывания. Матрица — [docs/verification/matrix.md](docs/verification/matrix.md).
