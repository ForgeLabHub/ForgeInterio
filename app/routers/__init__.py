"""HTTP-слой: по одному модулю на область ответственности."""
from . import admin, auth, pages, quiz

ROUTERS = (auth.router, quiz.router, admin.router, pages.router)

__all__ = ["ROUTERS", "admin", "auth", "pages", "quiz"]
