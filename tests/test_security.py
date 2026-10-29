"""Проверки, которые должны падать при возврате небезопасных умолчаний.

Каждая из них — регрессия на конкретную найденную проблему.
"""
from __future__ import annotations

import os
import re

import server  # noqa: E402  (импорт после настройки окружения)


def test_smtp_credentials_have_no_hardcoded_defaults():
    """Пароль приложения Gmail больше не зашит в код."""
    assert server.SMTP_USERNAME == "" or not server.SMTP_USERNAME.endswith("gmail.com")
    assert server.SMTP_PASSWORD == ""
    assert server.email_configured() is False


def test_admin_code_comes_from_the_environment():
    """Код админ-доступа читается из окружения, а не задан константой в коде."""
    assert os.environ["ADMIN_CODE"] == "test-admin-code"
    source = open("server.py", encoding="utf-8").read()
    # Ищем именно присваивание, а не упоминание в комментарии.
    assert not re.search(r'ADMIN_CODE\s*=\s*"', source), "код админ-доступа захардкожен"
    assert 'os.environ.get("ADMIN_CODE"' in source


def test_cors_does_not_allow_any_origin_with_credentials(client):
    """Ответ не должен подтверждать произвольный Origin при allow_credentials."""
    response = client.get("/", headers={"Origin": "https://evil.example"})
    assert response.headers.get("access-control-allow-origin") in (None, "")


def test_keep_alive_is_opt_in():
    """В тестах фоновый поток не поднимается и в сеть не ходит."""
    assert server.KEEP_ALIVE_ENABLED is False
