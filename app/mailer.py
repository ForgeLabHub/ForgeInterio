"""Отправка писем через SMTP.

Модуль задуман переносимым: он не знает ничего о предметной области. На вход —
тема, получатель, текст и вложения; конфигурация приходит из `config.settings()`.

Поведение при неполной конфигурации: письмо не отправляется, в лог пишется
причина, вызывающий код получает `False`. Ошибка почты никогда не ломает
основной запрос: заявка уже сохранена в базе.
"""
from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from .config import SmtpSettings, settings


@dataclass(frozen=True)
class Attachment:
    filename: str
    content: bytes
    maintype: str = "text"
    subtype: str = "plain"


class SmtpMailer:
    """Тонкая обёртка над `smtplib.SMTP_SSL` с предсказуемыми ошибками."""

    def __init__(self, config: SmtpSettings | None = None) -> None:
        self.config = config or settings().smtp

    @property
    def configured(self) -> bool:
        return self.config.configured

    def send(
        self,
        subject: str,
        to: str,
        body: str,
        attachments: list[Attachment] | None = None,
    ) -> bool:
        if not to:
            return False
        if not self.configured:
            print("SMTP не настроен: письмо не отправлено")
            return False

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.config.username
        msg["To"] = to
        msg.set_content(body)
        for item in attachments or []:
            msg.add_attachment(
                item.content,
                maintype=item.maintype,
                subtype=item.subtype,
                filename=item.filename,
            )

        try:
            with smtplib.SMTP_SSL(self.config.host, self.config.port) as server:
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
        except Exception as exc:  # noqa: BLE001 — сеть и SMTP отвечают чем угодно
            print(f"Ошибка при отправке письма: {exc}")
            return False
        print(f"Письмо успешно отправлено на {to}")
        return True


def send(subject: str, to: str, body: str, attachments: list[Attachment] | None = None) -> bool:
    """Короткий путь для одной отправки."""
    return SmtpMailer().send(subject, to, body, attachments)
