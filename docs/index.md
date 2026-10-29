# Документация Interio

| Вопрос | Документ |
| --- | --- |
| Запустить с нуля | [../BUILD.md](../BUILD.md) |
| Как устроено приложение | [architecture/system-context.md](architecture/system-context.md) |
| Где лежат данные | [database.md](database.md) |
| API и ошибки | [api/conventions.md](api/conventions.md) |
| Что делает модуль | [modules/](modules/) |
| Развёртывание | [operations/deployment.md](operations/deployment.md) |
| Наблюдаемость | [operations/monitoring.md](operations/monitoring.md) |
| **Секреты: что было исправлено** | [security/secrets.md](security/secrets.md) |
| Чем доказано, что работает | [verification/matrix.md](verification/matrix.md), CI |
| Что исправлено при аудите | [audit/portability-audit-2026-10-29.md](audit/portability-audit-2026-10-29.md) |
| English version | [en/index.md](en/index.md) · PDF в [pdf/](pdf/) |

## Правила

1. Утверждение без проверки — обещание: см. [verification/matrix.md](verification/matrix.md).
2. Секретов в коде нет. Конфигурация — только через окружение (`../.env.example`).
3. Тесты не ходят в сеть и не используют рабочую базу: `DB_PATH` подменяется в
   `tests/conftest.py`, `KEEP_ALIVE_ENABLED=false`.
4. Код разложен по модулям в пакете `app/` (`config`, `db`, `security`, `mailer`,
   `models`, `routers/*`); `server.py` — только сборка и запуск. Что и откуда
   заимствовать в другой проект: [modules/module-map.md](modules/module-map.md).

## Управление проектом

- `forge.sh` / `forge.bat` — запуск, остановка, логи, тесты, база и контейнеры одной командой; см. раздел в README.
