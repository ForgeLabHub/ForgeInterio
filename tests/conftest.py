"""Общая настройка тестов.

Приложение собирается из пакета `app`, поэтому окружение выставляется *до* импорта:
временная SQLite-база, отключённый keep-alive и явный код админ-доступа.
Каждый тест получает собственную базу: иначе состояние одного теста меняет
поведение следующего (именно так и была обнаружена ошибка «409 при регистрации»).
"""
from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["ENV"] = "test"
os.environ["KEEP_ALIVE_ENABLED"] = "false"
os.environ["ADMIN_CODE"] = "test-admin-code"
os.environ.pop("CORS_ORIGINS", None)


@pytest.fixture()
def client():
    """Клиент с чистой базой на каждый тест."""
    workspace = tempfile.mkdtemp(prefix="interio-test-")
    os.environ["DB_PATH"] = os.path.join(workspace, "test.db")

    import server

    importlib.reload(server)          # перечитывает DB_PATH и создаёт новый app
    server.init_db()

    from fastapi.testclient import TestClient

    with TestClient(server.app) as test_client:
        yield test_client
