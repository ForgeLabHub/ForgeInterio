"""Квиз: приём заявки и отправка копии на почту.

Здесь же живёт валидация предметных полей (телефон, email, обязательные шаги
квиза) — она относится к заявке, а не к аутентификации.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, BackgroundTasks, HTTPException

from .. import db, mailer
from ..models import QuizSubmissionRequest

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
REQUIRED_STEPS = (
    ("room_type", "тип помещения"),
    ("zones", "зоны помещения"),
    ("style", "стиль"),
    ("budget", "бюджет"),
)


def normalize_phone(raw: str) -> str:
    """+7XXXXXXXXXX из любого написания; ValueError, если номер не российский."""
    digits = re.sub(r"[^\d]", "", raw)
    if len(digits) != 11 or not digits.startswith(("7", "8")):
        raise ValueError("Некорректный формат телефона")
    return "+" + (digits if digits.startswith("7") else "7" + digits[1:])


def validate(payload: QuizSubmissionRequest) -> None:
    if not payload.name or not payload.phone or not payload.email:
        raise HTTPException(status_code=400, detail="Имя, телефон и email обязательны")
    if not EMAIL_RE.match(payload.email):
        raise HTTPException(status_code=400, detail="Введите корректный email адрес")

    missing = [title for field, title in REQUIRED_STEPS if not getattr(payload, field)]
    if missing:
        if len(missing) == 1:
            detail = f"Необходимо выбрать {missing[0]}"
        elif len(missing) == 2:
            detail = f"Необходимо выбрать {missing[0]} и {missing[1]}"
        else:
            detail = f"Необходимо выбрать {', '.join(missing[:-1])} и {missing[-1]}"
        raise HTTPException(status_code=400, detail=detail)

    if not payload.consent:
        raise HTTPException(status_code=400, detail="Необходимо согласие на обработку данных")


def preferences_text(payload: QuizSubmissionRequest) -> str:
    """Текст вложения: то, что человек увидит в письме."""
    lines = [
        "Заявка на дизайн-проект",
        "========================",
        "",
        f"Имя: {payload.name}",
        f"Телефон: {payload.phone}",
        f"Email: {payload.email}",
        f"Тип помещения: {payload.room_type}",
        f"Зоны: {', '.join(payload.zones) if payload.zones else 'Не указаны'}",
        f"Площадь: {payload.area} м²",
        f"Стиль: {payload.style}",
        f"Бюджет: {payload.budget}",
    ]
    if payload.comment:
        lines.append(f"Комментарий: {payload.comment}")
    return "\n".join(lines) + "\n"


def send_confirmation(payload: QuizSubmissionRequest) -> bool:
    body = (
        f"Здравствуйте, {payload.name}!\n\n"
        "Спасибо за заполнение формы на разработку вашего дизайн-проекта.\n"
        "Во вложении вы найдете текстовый файл с вашими ответами.\n\n"
        "Мы ознакомимся с вашей заявкой и свяжемся с вами в ближайшее время "
        "для обсуждения деталей!\n\n"
        "С уважением,\nКоманда Interio"
    )
    attachment = mailer.Attachment(
        filename="interio_preferences.txt",
        content=preferences_text(payload).encode("utf-8"),
    )
    return mailer.send(
        subject="Ваши ответы на квиз Interio",
        to=payload.email,
        body=body,
        attachments=[attachment],
    )


@router.post("/submit")
async def submit(payload: QuizSubmissionRequest, tasks: BackgroundTasks) -> dict:
    validate(payload)
    try:
        phone = normalize_phone(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = db.fetch_one("SELECT id FROM users WHERE phone = ?", (phone,))
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO quiz_submissions
            (name, phone, email, room_type, zones, area, style, budget, comment, consent, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                phone,
                payload.email,
                payload.room_type,
                ",".join(payload.zones) if payload.zones else "",
                payload.area,
                payload.style,
                payload.budget,
                payload.comment,
                payload.consent,
                user["id"] if user else None,
            ),
        )
        submission_id = cur.lastrowid

    print(f"Заявка квиза #{submission_id} успешно сохранена")
    # Письмо не должно задерживать ответ: отправка идёт после сохранения заявки.
    tasks.add_task(send_confirmation, payload)
    return {"success": True, "submission_id": submission_id, "message": "Заявка успешно сохранена"}


@router.get("/submissions")
async def submissions() -> dict:
    rows = db.fetch_all(
        """
        SELECT qs.*, u.nickname as user_nickname
        FROM quiz_submissions qs
        LEFT JOIN users u ON qs.user_id = u.id
        ORDER BY qs.created_at DESC
        LIMIT 50
        """
    )
    return {"submissions": [dict(row) for row in rows]}
