"""Проверки, которые должны падать при возврате небезопасных умолчаний.

Каждая из них — регрессия на конкретную найденную проблему. После разбиения
`server.py` на модули проверки смотрят на пакет `app/`, но смысл тот же: ни
один секрет не должен снова появиться в коде.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from app.config import settings

ROOT = Path(__file__).resolve().parent.parent
SOURCES = sorted((ROOT / "app").rglob("*.py")) + [ROOT / "server.py"]


def _source_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in SOURCES)


def test_smtp_credentials_have_no_hardcoded_defaults():
    """Пароль приложения Gmail больше не зашит в код."""
    smtp = settings().smtp
    assert smtp.username == "" or not smtp.username.endswith("gmail.com")
    assert smtp.password == ""
    assert smtp.configured is False


def test_admin_code_comes_from_the_environment():
    """Код админ-доступа читается из окружения, а не задан константой в коде."""
    assert os.environ["ADMIN_CODE"] == "test-admin-code"
    source = _source_text()
    # Ищем именно присваивание, а не упоминание в комментарии.
    assert not re.search(r'ADMIN_CODE\s*=\s*"', source), "код админ-доступа захардкожен"
    assert 'os.environ.get("ADMIN_CODE"' in source


def test_cors_does_not_allow_any_origin_with_credentials(client):
    """Ответ не должен подтверждать произвольный Origin при allow_credentials."""
    response = client.get("/", headers={"Origin": "https://evil.example"})
    assert response.headers.get("access-control-allow-origin") in (None, "")


def test_keep_alive_is_opt_in():
    """В тестах фоновый поток не поднимается и в сеть не ходит."""
    assert settings().keep_alive_enabled is False
    assert settings().is_test is True
