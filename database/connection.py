import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from database.config import get_database_url, is_postgres_enabled


def _sqlite_url_to_path() -> str:
    url = get_database_url()
    if url.startswith("sqlite://"):
        sqlite_path = url.replace("sqlite:///", "", 1)
        return sqlite_path
    return ""


@contextmanager
def get_db_connection() -> Iterator[psycopg.connection.Connection]:
    if is_postgres_enabled():
        conn = psycopg.connect(get_database_url(), row_factory=dict_row)
        try:
            yield conn
        finally:
            conn.close()
        return

    sqlite_path = _sqlite_url_to_path()
    if not sqlite_path:
        raise RuntimeError("Database URL is not configured for SQLite fallback.")

    import sqlite3

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_postgres_schema() -> None:
    if not is_postgres_enabled():
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    company_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL UNIQUE,
                    company_details TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'HR',
                    account_status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_role_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    company_id TEXT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
                    role_name TEXT NOT NULL,
                    assigned_by TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (user_id, company_id, role_name)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    setting_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    company_id TEXT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
                    preferences JSONB,
                    dashboard_settings JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (user_id, company_id)
                );
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_roles_company_id ON user_roles(company_id);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_settings_company_id ON user_settings(company_id);"
            )
            conn.commit()
