"""Админские операции: список заявок и смена статуса."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import db, security
from ..models import StatusUpdateRequest

router = APIRouter(prefix="/api/admin", tags=["admin"])

ALLOWED_STATUSES = ("new", "contacted", "in_progress", "completed", "cancelled")


@router.get("/submissions")
async def submissions(admin: dict = Depends(security.require_admin)) -> dict:
    rows = db.fetch_all(
        """
        SELECT qs.*, u.nickname as user_nickname
        FROM quiz_submissions qs
        LEFT JOIN users u ON qs.user_id = u.id
        ORDER BY qs.created_at DESC
        LIMIT 100
        """
    )
    return {"success": True, "submissions": [dict(row) for row in rows]}


@router.put("/submissions/{submission_id}")
async def update_status(
    submission_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    admin: dict = Depends(security.require_admin),
) -> dict:
    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Неверный статус")

    with db.cursor() as cur:
        cur.execute(
            "UPDATE quiz_submissions SET status = ? WHERE id = ?",
            (payload.status, submission_id),
        )
        updated = cur.rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return {
        "success": True,
        "message": f"Статус заявки {submission_id} обновлен на {payload.status}",
    }
