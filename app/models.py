"""Pydantic-модели запросов и ответов.

Отдельный модуль, чтобы контракт API читался в одном месте и не был размазан по
обработчикам: те же модели экспортируются в OpenAPI (`/docs`).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class PhoneCheckRequest(BaseModel):
    phone: str


class LoginRequest(BaseModel):
    phone: str
    password: str


class RegisterRequest(BaseModel):
    phone: str
    nickname: str
    password: str


class SessionRequest(BaseModel):
    session_id: str


class AdminLoginRequest(BaseModel):
    code: str


class QuizSubmissionRequest(BaseModel):
    name: str
    phone: str
    email: str
    room_type: str
    zones: list[str] = Field(default_factory=list)
    area: int
    style: str
    budget: str
    comment: str | None = None
    consent: bool


class UserResponse(BaseModel):
    id: int
    phone: str
    nickname: str
    created_at: str


class StatusUpdateRequest(BaseModel):
    status: str
