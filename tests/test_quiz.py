"""Квиз: валидация заявки и доступ к админским данным."""
from __future__ import annotations

VALID = {
    "name": "Анна",
    "phone": "+79991234567",
    "email": "anna@example.com",
    "room_type": "квартира",
    "zones": ["кухня"],
    "area": 60,
    "style": "лофт",
    "budget": "1-2 млн",
    "consent": True,
}


def test_valid_submission_is_accepted(client):
    response = client.post("/api/quiz/submit", json=VALID)
    assert response.status_code == 200, response.text


def test_consent_is_mandatory(client):
    payload = dict(VALID, consent=False)
    response = client.post("/api/quiz/submit", json=payload)
    assert response.status_code == 400
    assert "согласие" in response.json()["detail"].lower()


def test_email_format_is_validated(client):
    payload = dict(VALID, email="not-an-email")
    response = client.post("/api/quiz/submit", json=payload)
    assert response.status_code == 400


def test_phone_format_is_validated(client):
    payload = dict(VALID, phone="123")
    response = client.post("/api/quiz/submit", json=payload)
    assert response.status_code == 400


def test_admin_submissions_are_not_public(client):
    response = client.get("/api/admin/submissions")
    assert response.status_code in (401, 403)
