"""Пароли, сессии и проверка прав.

Модуль самостоятелен: пароли — `hashlib`, токены — `secrets`, сессии — запись в
таблице `sessions`. Его можно перенести в другой проект, заменив только
`db.cursor` на свой доступ к базе.
"""
from __future__ import annotations

import hashlib
import secrets
import time

from fastapi import HTTPException, Request, Response

from . import db
from .config import settings

MIN_PASSWORD_LENGTH = 8
SESSION_TTL_SECONDS = 3600 * 24 * 7  # неделя


def hash_password(password: str) -> str:
    """Хеш пароля.

    Внимание: SHA-256 без соли — совместимость с уже сохранёнными паролями.
    Для нового проекта берите `argon2` или `bcrypt` (см.
    docs/security/secrets.md и docs/modules/auth.md).
    """
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Пароль должен содержать минимум {MIN_PASSWORD_LENGTH} символов",
        )
    if not any(c.isalpha() for c in password):
        raise HTTPException(status_code=400, detail="Пароль должен содержать минимум одну букву")
    return password


def create_session(user_id: int) -> str:
    """Запись сессии в базе; возвращает токен для cookie."""
    token = secrets.token_hex(16)
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (session_token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at),
        )
    return token


def set_session_cookie(response: Response, session_token: str) -> None:
    """Cookie сессии: httpOnly, SameSite=Lax, на весь сайт."""
    response.set_cookie(
        key="session_id",
        value=session_token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key="session_id", path="/")


def session_user(token: str | None) -> dict | None:
    """Пользователь по токену сессии или None, если сессии нет или она истекла."""
    if not token:
        return None
    row = db.fetch_one(
        """
        SELECT u.id, u.phone, u.nickname, u.role FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.expires_at > ?
        """,
        (token, int(time.time())),
    )
    if not row:
        return None
    return {"id": row["id"], "phone": row["phone"], "nickname": row["nickname"], "role": row["role"]}


def get_current_admin_user(request: Request) -> dict | None:
    user = session_user(request.cookies.get("session_id"))
    return user if user and user.get("role") == "admin" else None


def require_admin(request: Request) -> dict:
    """Зависимость FastAPI: 403, если вошедший пользователь не администратор."""
    user = get_current_admin_user(request)
    if not user:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return user


def check_admin_code(code: str) -> None:
    """Проверка кода админ-доступа.

    Код приходит из окружения. Пустой код = админ-вход выключен (503), а не
    «пускаем всех»: раньше в коде был захардкожен `ADMIN123`, и это была
    готовая эскалация привилегий. Сравнение — постоянного времени.
    """
    admin_code = settings().admin_code
    if not admin_code:
        raise HTTPException(
            status_code=503,
            detail="Админ-вход не настроен: задайте ADMIN_CODE в окружении",
        )
    if not secrets.compare_digest(code, admin_code):
        raise HTTPException(status_code=401, detail="Неверный код")
