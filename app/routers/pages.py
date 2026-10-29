"""HTML-страницы и заглушки состояния сессии для фронтенда."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

from ..models import SessionRequest

router = APIRouter(tags=["pages"])

TEMPLATES = {
    "/": "templates/index.html",
    "/admin": "templates/admin.html",
    "/quiz": "templates/quiz.html",
}


def _page(path: str) -> FileResponse:
    return FileResponse(path)


@router.get("/", response_class=FileResponse, include_in_schema=False)
async def index() -> FileResponse:
    return _page(TEMPLATES["/"])


@router.get("/admin", response_class=FileResponse, include_in_schema=False)
async def admin_page() -> FileResponse:
    return _page(TEMPLATES["/admin"])


@router.get("/quiz", response_class=FileResponse, include_in_schema=False)
async def quiz_page() -> FileResponse:
    return _page(TEMPLATES["/quiz"])


@router.post("/api/session/data")
async def session_data(payload: SessionRequest) -> dict:
    """Данные сессии StateManager.

    Хранилища на сервере нет — состояние живёт в браузере. Контракт оставлен,
    чтобы старый фронтенд не получал 404.
    """
    return {
        "success": True,
        "session_id": payload.session_id,
        "data": None,
        "message": "Данные сессии получены",
    }


@router.post("/api/session/save")
async def session_save(payload: SessionRequest) -> dict:
    print(f"Сохранение данных сессии: {payload.session_id}")
    return {"success": True, "message": "Данные сессии сохранены"}
