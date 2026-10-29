"""Доступ к SQLite.

Одно место, где открывается соединение и создаётся схема. Модуль можно
забрать в другой проект целиком: зависимости — только стандартная библиотека
(`sqlite3`), путь к файлу приходит снаружи.

Схема создаётся идемпотентно (`CREATE TABLE IF NOT EXISTS` + `ALTER TABLE` в
`try/except`): приложение обновляется на живой базе, отдельного шага миграции у
SQLite-проекта нет.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from .config import db_path

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        nickname TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_token TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS quiz_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        room_type TEXT NOT NULL,
        zones TEXT NOT NULL,
        area INTEGER NOT NULL,
        style TEXT NOT NULL,
        budget TEXT NOT NULL,
        comment TEXT,
        consent BOOLEAN NOT NULL,
        user_id INTEGER,
        status TEXT DEFAULT 'new',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,
)

# Колонки, добавленные позже: старые базы догоняются без потери данных.
ADDED_COLUMNS = (
    ("users", "role", "TEXT DEFAULT 'user'"),
    ("quiz_submissions", "status", "TEXT DEFAULT 'new'"),
)


def connect(path: str | None = None) -> sqlite3.Connection:
    """Соединение с доступом к колонкам по имени."""
    conn = sqlite3.connect(path or db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str | None = None) -> None:
    """Создать схему и догнать базу до текущей версии."""
    conn = connect(path)
    try:
        cursor = conn.cursor()
        for statement in SCHEMA:
            cursor.execute(statement)
        for table, column, ddl in ADDED_COLUMNS:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
            except sqlite3.OperationalError:
                pass  # колонка уже есть — это нормальный путь обновления
        conn.commit()
    finally:
        conn.close()


@contextmanager
def cursor(path: str | None = None) -> Iterator[sqlite3.Cursor]:
    """Курсор с коммитом при успехе и закрытием в любом случае.

    Заменяет повторяющиеся `conn = ...; cursor = ...; conn.commit();
    conn.close()`: закрытие гарантировано, в том числе при исключении.
    """
    conn = connect(path)
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


def fetch_one(sql: str, params: tuple = (), path: str | None = None) -> sqlite3.Row | None:
    with cursor(path) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: tuple = (), path: str | None = None) -> list[sqlite3.Row]:
    with cursor(path) as cur:
        cur.execute(sql, params)
        return cur.fetchall()
