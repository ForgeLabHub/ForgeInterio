"""Конфигурация приложения.

Все значения читаются из окружения **в момент вызова**, а не один раз при
импорте: тесты подменяют `DB_PATH` между тестами, а `forge.sh env set` меняет
`.env` без перезапуска интерпретатора. Один источник правды — `settings()`.

Значения по умолчанию безопасны: без настроек приложение поднимается и
работает, а отключаются только те возможности, которые без настроек
небезопасны или бессмысленны (админ-вход, почта, keep-alive).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class SmtpSettings:
    host: str
    port: int
    username: str
    password: str

    @property
    def configured(self) -> bool:
        return bool(self.username and self.password)


@dataclass(frozen=True)
class Settings:
    db_path: str
    cors_origins: tuple[str, ...]
    admin_code: str
    smtp: SmtpSettings
    app_url: str
    keep_alive_enabled: bool
    env: str

    @property
    def is_test(self) -> bool:
        return self.env == "test"


def settings() -> Settings:
    raw_origins = os.environ.get("CORS_ORIGINS", "")
    origins = tuple(o.strip() for o in raw_origins.split(",") if o.strip())
    try:
        smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    except ValueError:
        smtp_port = 465
    return Settings(
        db_path=os.environ.get("DB_PATH", "data.db"),
        cors_origins=origins,
        admin_code=os.environ.get("ADMIN_CODE", ""),
        smtp=SmtpSettings(
            host=os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
            port=smtp_port,
            username=os.environ.get("SMTP_USERNAME", ""),
            password=os.environ.get("SMTP_PASSWORD", ""),
        ),
        app_url=os.environ.get("APP_URL", "https://interio-0foc.onrender.com/"),
        keep_alive_enabled=_bool("KEEP_ALIVE_ENABLED"),
        env=os.environ.get("ENV", "development"),
    )


def db_path() -> str:
    return settings().db_path


def server_address() -> tuple[str, int, bool]:
    """Хост, порт и режим автоперезагрузки для `python server.py`.

    Платформа сама назначает PORT (Render, Railway, контейнер), поэтому адрес
    берётся из окружения. RELOAD=1 нужен только в разработке: в CI и в проде
    перезагрузка мешает остановке процесса.
    """
    try:
        port = int(os.environ.get("PORT", "8000"))
    except ValueError:
        port = 8000
    return os.environ.get("HOST", "0.0.0.0"), port, _bool("RELOAD")
