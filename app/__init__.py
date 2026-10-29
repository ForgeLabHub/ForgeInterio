"""Приложение Interio как набор модулей.

Точка сборки — `create_app()`. Приложение собирается из независимых частей:
конфигурация (`config`), база (`db`), безопасность (`security`), почта
(`mailer`), контракты (`models`) и HTTP-слой (`routers`). Каждый модуль можно
забрать в другой проект по отдельности — см. docs/modules/module-map.md.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config, keepalive
from .db import init_db
from .routers import ROUTERS

__version__ = "1.1.0"


def create_app() -> FastAPI:
    settings = config.settings()
    app = FastAPI(title="Interio API", version=__version__)

    # CORS: список источников из окружения. Раньше здесь были "*" вместе с
    # allow_credentials=True — комбинация, которая разрешала любому сайту
    # присылать cookie-сессии. Пустой список = только свой origin.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Requested-With"],
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.on_event("startup")
    async def _startup() -> None:
        init_db()
        keepalive.start_if_enabled()

    for router in ROUTERS:
        app.include_router(router)

    return app
