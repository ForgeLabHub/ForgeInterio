"""Точка входа: `python server.py`.

Сам код приложения живёт в пакете `app/`: конфигурация, база, безопасность,
почта и роутеры разнесены по модулям, чтобы их можно было переиспользовать
(см. docs/modules/module-map.md). Здесь остаётся только сборка и запуск.

Прежний контракт сохранён: `from server import app` и `uvicorn server:app`
работают так же, как раньше, `server.init_db()` — тоже.
"""
from __future__ import annotations

import uvicorn

from app import create_app
from app.config import server_address
from app.db import init_db

app = create_app()

__all__ = ["app", "init_db"]


if __name__ == "__main__":
    host, port, reload = server_address()
    uvicorn.run("server:app", host=host, port=port, reload=reload)
