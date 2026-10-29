"""Аутентификация и сессии: поведение, а не реализация."""
from __future__ import annotations


def register(client, phone="+79991234567", nickname="tester", password="secret123"):
    return client.post(
        "/api/auth/register",
        json={"phone": phone, "nickname": nickname, "password": password},
    )


def test_register_creates_a_session(client):
    response = register(client)
    assert response.status_code == 200, response.text
    assert response.json()["success"] is True
    assert client.cookies.get("session_id")


def test_current_user_reflects_the_session(client):
    register(client)
    current = client.get("/api/auth/current-user")
    assert current.json()["success"] is True
    assert current.json()["user"]["nickname"] == "tester"


def test_duplicate_phone_is_rejected(client):
    register(client)
    second = register(client, nickname="other")
    assert second.status_code == 409
    assert "телефон" in second.json()["detail"].lower()


def test_weak_password_is_rejected(client):
    response = register(client, password="short")
    assert response.status_code == 400
    assert "8" in response.json()["detail"]


def test_logout_invalidates_the_session(client):
    register(client)
    client.post("/api/auth/logout")
    assert client.get("/api/auth/current-user").json()["success"] is False


def test_admin_login_requires_the_configured_code(client):
    register(client)
    wrong = client.post("/api/auth/admin-login", json={"code": "ADMIN123"})
    assert wrong.status_code == 401
    right = client.post("/api/auth/admin-login", json={"code": "test-admin-code"})
    assert right.status_code == 200
