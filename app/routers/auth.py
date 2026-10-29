"""Регистрация, вход, выход и текущий пользователь."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from .. import db, security
from ..models import AdminLoginRequest, LoginRequest, PhoneCheckRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/check-phone")
async def check_phone(payload: PhoneCheckRequest) -> dict:
    """Занят ли номер: до регистрации, чтобы не гонять пользователя по кругу."""
    phone = payload.phone.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Номер телефона обязателен")
    row = db.fetch_one("SELECT id FROM users WHERE phone = ?", (phone,))
    return {"exists": row is not None, "phone": phone}


@router.post("/login")
async def login(payload: LoginRequest, response: Response) -> dict:
    phone = payload.phone.strip()
    if not phone or not payload.password:
        raise HTTPException(status_code=400, detail="Телефон и пароль обязательны")

    user = db.fetch_one(
        "SELECT * FROM users WHERE phone = ? AND password_hash = ?",
        (phone, security.hash_password(payload.password)),
    )
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    token = security.create_session(user["id"])
    security.set_session_cookie(response, token)
    return {
        "success": True,
        "user": {"id": user["id"], "phone": user["phone"], "nickname": user["nickname"]},
    }


@router.post("/register")
async def register(payload: RegisterRequest, response: Response) -> dict:
    phone = payload.phone.strip()
    nickname = payload.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=400, detail="Никнейм обязателен")
    password = security.validate_password(payload.password)

    existing = db.fetch_one(
        "SELECT id, phone, nickname FROM users WHERE phone = ? OR nickname = ?",
        (phone, nickname),
    )
    if existing:
        if existing["phone"] == phone:
            raise HTTPException(status_code=409, detail="Этот номер телефона уже зарегистрирован")
        raise HTTPException(status_code=409, detail="Этот никнейм уже занят")

    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO users (phone, nickname, password_hash) VALUES (?, ?, ?)",
            (phone, nickname, security.hash_password(password)),
        )
        user_id = cur.lastrowid

    token = security.create_session(user_id)
    security.set_session_cookie(response, token)
    return {"success": True, "user": {"id": user_id, "phone": phone, "nickname": nickname}}


@router.post("/admin-login")
async def admin_login(payload: AdminLoginRequest, request: Request) -> dict:
    """Повышение роли по коду из окружения (ADMIN_CODE)."""
    security.check_admin_code(payload.code)

    user = security.session_user(request.cookies.get("session_id"))
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    with db.cursor() as cur:
        cur.execute("UPDATE users SET role = ? WHERE id = ?", ("admin", user["id"]))
    return {"success": True, "message": "Доступ к админ панели предоставлен"}


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict:
    token = request.cookies.get("session_id")
    if token:
        with db.cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE session_token = ?", (token,))
    security.clear_session_cookie(response)
    return {"success": True}


@router.get("/current-user")
async def current_user(request: Request) -> dict:
    user = security.session_user(request.cookies.get("session_id"))
    if not user:
        return {"success": False, "user": None}
    return {
        "success": True,
        "user": {"id": user["id"], "phone": user["phone"], "nickname": user["nickname"]},
    }


@router.get("/users", response_model=dict)
async def list_users() -> dict:
    """Список пользователей для отладки (без хешей паролей)."""
    rows = db.fetch_all(
        "SELECT id, phone, nickname, created_at FROM users ORDER BY created_at DESC"
    )
    return {"users": [UserResponse(**dict(row)).model_dump() for row in rows]}
