import os
import re
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import bcrypt

from database.config import get_database_url, is_postgres_enabled
from database.connection import init_postgres_schema

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "auth.db"


def _connect():
    if is_postgres_enabled():
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(get_database_url(), row_factory=dict_row)

    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_auth_db() -> None:
    if is_postgres_enabled():
        init_postgres_schema()
        return

    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                company_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL UNIQUE,
                company_details TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                company_id TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'HR',
                account_status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(company_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_roles (
                user_role_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company_id TEXT NOT NULL,
                role_name TEXT NOT NULL,
                assigned_by TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, company_id, role_name),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(company_id) REFERENCES companies(company_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company_id TEXT NOT NULL,
                preferences TEXT,
                dashboard_settings TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, company_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(company_id) REFERENCES companies(company_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(company_id) REFERENCES companies(company_id)
            )
            """
        )

        company_cols = {row[1] for row in conn.execute("PRAGMA table_info(companies)").fetchall()}
        if "company_details" not in company_cols:
            conn.execute("ALTER TABLE companies ADD COLUMN company_details TEXT")
        if "updated_at" not in company_cols:
            conn.execute("ALTER TABLE companies ADD COLUMN updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")

        user_cols = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "account_status" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN account_status TEXT NOT NULL DEFAULT 'active'")
        if "updated_at" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")

        conn.commit()
    finally:
        conn.close()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _company_id() -> str:
    return f"CMP-{uuid.uuid4().hex[:10].upper()}"


def _user_id() -> str:
    return f"USR-{uuid.uuid4().hex[:10].upper()}"


def _session_id() -> str:
    return secrets.token_urlsafe(32)


def _setting_id() -> str:
    return f"SET-{uuid.uuid4().hex[:12].upper()}"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def password_requirements(password: str) -> Dict[str, bool]:
    return {
        "min_8_chars": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "special_char": bool(re.search(r"[^A-Za-z0-9]", password)),
    }


def _password_meets_policy(password: str) -> bool:
    requirements = password_requirements(password)
    return all(requirements.values())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            return True
        if password.endswith(".") and bcrypt.checkpw(password[:-1].encode("utf-8"), password_hash.encode("utf-8")):
            return True
        if not password.endswith(".") and bcrypt.checkpw((password + ".").encode("utf-8"), password_hash.encode("utf-8")):
            return True
        return False
    except (ValueError, TypeError):
        return False


def _role_name_for_user(conn, user_id: str, company_id: str) -> str:
    if is_postgres_enabled():
        row = conn.execute(
            "SELECT role_name FROM user_roles WHERE user_id = %s AND company_id = %s ORDER BY created_at LIMIT 1",
            (user_id, company_id),
        ).fetchone()
        if row:
            return row["role_name"]
    else:
        row = conn.execute(
            "SELECT role_name FROM user_roles WHERE user_id = ? AND company_id = ? ORDER BY created_at LIMIT 1",
            (user_id, company_id),
        ).fetchone()
        if row:
            return row["role_name"]

    row = conn.execute(
        "SELECT role FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone() if not is_postgres_enabled() else conn.execute(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,),
    ).fetchone()
    if row:
        return row["role"] if isinstance(row, dict) else row[1]
    return "HR"


def _save_default_user_role(conn, user_id: str, company_id: str, role_name: str = "HR") -> None:
    if is_postgres_enabled():
        conn.execute(
            "INSERT INTO user_roles (user_role_id, user_id, company_id, role_name, assigned_by, created_at) VALUES (%s, %s, %s, %s, %s, NOW()) ON CONFLICT (user_id, company_id, role_name) DO NOTHING",
            (f"ROLE-{uuid.uuid4().hex[:12].upper()}", user_id, company_id, role_name, user_id),
        )
    else:
        conn.execute(
            "INSERT OR IGNORE INTO user_roles (user_role_id, user_id, company_id, role_name, assigned_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (f"ROLE-{uuid.uuid4().hex[:12].upper()}", user_id, company_id, role_name, user_id, _iso(_now_utc())),
        )


def register_company(company_name: str, full_name: str, email: str, password: str, confirm_password: str) -> Dict[str, str]:
    if not company_name or not company_name.strip():
        raise ValueError("Company name is required.")
    if not full_name or not full_name.strip():
        raise ValueError("HR user's full name is required.")

    normalized_email = _normalize_email(email)
    if not normalized_email or "@" not in normalized_email:
        raise ValueError("A valid work email is required.")
    if not _password_meets_policy(password):
        requirements = password_requirements(password)
        missing = [
            "at least 8 characters",
            "an uppercase letter",
            "a lowercase letter",
            "a special character",
        ]
        missing = [
            msg for msg, ok in zip(missing, [
                requirements["min_8_chars"],
                requirements["uppercase"],
                requirements["lowercase"],
                requirements["special_char"],
            ]) if not ok
        ]
        raise ValueError("Password must include: " + ", ".join(missing) + ".")
    if password != confirm_password:
        raise ValueError("Passwords do not match.")

    init_auth_db()
    conn = _connect()
    try:
        if is_postgres_enabled():
            existing_company = conn.execute(
                "SELECT company_id FROM companies WHERE lower(company_name) = lower(%s)",
                (company_name.strip(),),
            ).fetchone()
            existing_user = conn.execute(
                "SELECT user_id FROM users WHERE lower(email) = lower(%s)",
                (normalized_email,),
            ).fetchone()
        else:
            conn.execute("BEGIN IMMEDIATE")
            existing_company = conn.execute(
                "SELECT company_id FROM companies WHERE company_name = ? COLLATE NOCASE",
                (company_name.strip(),),
            ).fetchone()
            existing_user = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (normalized_email,),
            ).fetchone()

        if existing_company:
            raise ValueError("A company with this name is already registered.")
        if existing_user:
            raise ValueError("An account with this email already exists.")

        company_id = _company_id()
        user_id = _user_id()
        now = _iso(_now_utc())
        company_hash = hash_password(password)

        if is_postgres_enabled():
            conn.execute(
                "INSERT INTO companies (company_id, company_name, company_details, status, created_at, updated_at) VALUES (%s, %s, %s, 'active', NOW(), NOW())",
                (company_id, company_name.strip(), f"Workspace for {company_name.strip()}"),
            )
            conn.execute(
                "INSERT INTO users (user_id, company_id, full_name, email, password_hash, role, account_status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, 'HR', 'active', NOW(), NOW())",
                (user_id, company_id, full_name.strip(), normalized_email, company_hash),
            )
            conn.execute(
                "INSERT INTO user_roles (user_role_id, user_id, company_id, role_name, assigned_by, created_at) VALUES (%s, %s, %s, 'HR', %s, NOW())",
                (f"ROLE-{uuid.uuid4().hex[:12].upper()}", user_id, company_id, user_id),
            )
        else:
            conn.execute(
                "INSERT INTO companies (company_id, company_name, company_details, status, created_at, updated_at) VALUES (?, ?, ?, 'active', ?, ?)",
                (company_id, company_name.strip(), f"Workspace for {company_name.strip()}", now, now),
            )
            conn.execute(
                "INSERT INTO users (user_id, company_id, full_name, email, password_hash, role, account_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'HR', 'active', ?, ?)",
                (user_id, company_id, full_name.strip(), normalized_email, company_hash, now, now),
            )
            conn.execute(
                "INSERT INTO user_roles (user_role_id, user_id, company_id, role_name, assigned_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (f"ROLE-{uuid.uuid4().hex[:12].upper()}", user_id, company_id, 'HR', user_id, now),
            )

        conn.commit()
        return {
            "company_id": company_id,
            "user_id": user_id,
            "company_name": company_name.strip(),
            "email": normalized_email,
        }
    except Exception:
        if not is_postgres_enabled():
            conn.rollback()
        raise
    finally:
        conn.close()


def login_user(email: str, password: str) -> Dict[str, Any]:
    if not email or not password:
        raise ValueError("Email and password are required.")

    normalized_email = _normalize_email(email)
    init_auth_db()
    conn = _connect()
    try:
        if is_postgres_enabled():
            user_row = conn.execute(
                "SELECT * FROM users WHERE lower(email) = lower(%s) AND account_status = 'active'",
                (normalized_email,),
            ).fetchone()
        else:
            user_row = conn.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE AND account_status = 'active'",
                (normalized_email,),
            ).fetchone()

        if not user_row:
            raise ValueError("Invalid email or password.")

        if not verify_password(password, user_row["password_hash"]):
            raise ValueError("Invalid email or password.")

        token = _session_id()
        expires_at = _iso(_now_utc() + timedelta(days=7))
        now = _iso(_now_utc())

        if is_postgres_enabled():
            conn.execute(
                "INSERT INTO sessions (session_id, user_id, company_id, expires_at, revoked, created_at) VALUES (%s, %s, %s, %s, 0, NOW())",
                (token, user_row["user_id"], user_row["company_id"], expires_at),
            )
        else:
            conn.execute(
                "INSERT INTO sessions (session_id, user_id, company_id, expires_at, revoked, created_at) VALUES (?, ?, ?, ?, 0, ?)",
                (token, user_row["user_id"], user_row["company_id"], expires_at, now),
            )
        conn.commit()

        company_row = conn.execute(
            "SELECT company_name FROM companies WHERE company_id = %s" if is_postgres_enabled() else "SELECT company_name FROM companies WHERE company_id = ?",
            (user_row["company_id"],),
        ).fetchone()

        role_name = _role_name_for_user(conn, user_row["user_id"], user_row["company_id"])
        return {
            "token": token,
            "user_id": user_row["user_id"],
            "company_id": user_row["company_id"],
            "company_name": company_row["company_name"] if company_row else "Company",
            "full_name": user_row["full_name"],
            "email": user_row["email"],
            "role": role_name,
            "expires_at": expires_at,
        }
    finally:
        conn.close()


def get_session_context(session_token: str) -> Optional[Dict[str, Any]]:
    if not session_token or not isinstance(session_token, str) or not str(session_token).strip():
        return None
    session_token = str(session_token).strip()

    init_auth_db()
    conn = _connect()
    try:
        now = _now_utc()
        if is_postgres_enabled():
            row = conn.execute(
                """
                SELECT s.session_id, s.user_id, s.company_id, s.expires_at, s.revoked,
                       u.full_name, u.email
                FROM sessions s
                INNER JOIN users u ON u.user_id = s.user_id
                WHERE s.session_id = %s AND s.revoked = 0
                """,
                (session_token,),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT s.session_id, s.user_id, s.company_id, s.expires_at, s.revoked,
                       u.full_name, u.email, u.role
                FROM sessions s
                INNER JOIN users u ON u.user_id = s.user_id
                WHERE s.session_id = ? AND s.revoked = 0
                """,
                (session_token,),
            ).fetchone()

        if not row:
            return None

        expires_at = datetime.fromisoformat(str(row["expires_at"])) if isinstance(row["expires_at"], str) else row["expires_at"]
        expires_at = expires_at.astimezone(timezone.utc)
        if expires_at <= now:
            conn.execute(
                "UPDATE sessions SET revoked = 1 WHERE session_id = %s" if is_postgres_enabled() else "UPDATE sessions SET revoked = 1 WHERE session_id = ?",
                (session_token,),
            )
            conn.commit()
            return None

        role_name = _role_name_for_user(conn, row["user_id"], row["company_id"])
        return {
            "session_id": row["session_id"],
            "user_id": row["user_id"],
            "company_id": row["company_id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": role_name,
        }
    finally:
        conn.close()


def logout_session(session_token: str) -> bool:
    if not session_token or not isinstance(session_token, str) or not str(session_token).strip():
        return False
    session_token = str(session_token).strip()

    conn = _connect()
    try:
        result = conn.execute(
            "UPDATE sessions SET revoked = 1 WHERE session_id = %s AND revoked = 0" if is_postgres_enabled() else "UPDATE sessions SET revoked = 1 WHERE session_id = ? AND revoked = 0",
            (session_token,),
        )
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        if is_postgres_enabled():
            row = conn.execute(
                """
                SELECT u.user_id, u.company_id, u.full_name, u.email, u.role AS role_name, u.account_status as status, u.created_at,
                       c.company_name
                FROM users u
                INNER JOIN companies c ON c.company_id = u.company_id
                WHERE u.user_id = %s
                """,
                (user_id,),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT u.user_id, u.company_id, u.full_name, u.email, u.role, u.account_status as status, u.created_at,
                       c.company_name
                FROM users u
                INNER JOIN companies c ON c.company_id = u.company_id
                WHERE u.user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if not row:
            return None
        role = row["role_name"] if isinstance(row, dict) and "role_name" in row else row["role"]
        return {
            "user_id": row["user_id"],
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": role,
            "status": row["status"],
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def update_user_profile(user_id: str, full_name: str | None = None) -> Dict[str, Any]:
    if full_name is not None and (not full_name.strip()):
        raise ValueError("Full name cannot be empty.")

    conn = _connect()
    try:
        if is_postgres_enabled():
            existing = conn.execute("SELECT user_id, full_name FROM users WHERE user_id = %s", (user_id,)).fetchone()
            if not existing:
                raise ValueError("User not found.")
            updated_name = full_name.strip() if full_name is not None else existing["full_name"]
            conn.execute(
                "UPDATE users SET full_name = %s, updated_at = NOW() WHERE user_id = %s",
                (updated_name, user_id),
            )
        else:
            existing = conn.execute("SELECT user_id, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if not existing:
                raise ValueError("User not found.")
            updated_name = full_name.strip() if full_name is not None else existing["full_name"]
            conn.execute(
                "UPDATE users SET full_name = ? WHERE user_id = ?",
                (updated_name, user_id),
            )
        conn.commit()
        return {"user_id": user_id, "full_name": updated_name}
    finally:
        conn.close()


def change_user_password(user_id: str, current_password: str, new_password: str, confirm_password: str) -> None:
    if not current_password or not new_password or not confirm_password:
        raise ValueError("Current password and new password are required.")
    if new_password != confirm_password:
        raise ValueError("New password and confirmation do not match.")
    if not _password_meets_policy(new_password):
        requirements = password_requirements(new_password)
        missing = [
            "at least 8 characters",
            "an uppercase letter",
            "a lowercase letter",
            "a special character",
        ]
        missing = [label for label, ok in zip(missing, [requirements["min_8_chars"], requirements["uppercase"], requirements["lowercase"], requirements["special_char"]]) if not ok]
        raise ValueError("New password must include: " + ", ".join(missing) + ".")

    conn = _connect()
    try:
        if is_postgres_enabled():
            user_row = conn.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_id,)).fetchone()
            if not user_row:
                raise ValueError("User not found.")
            if not verify_password(current_password, user_row["password_hash"]):
                raise ValueError("Current password is incorrect.")
            conn.execute(
                "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE user_id = %s",
                (hash_password(new_password), user_id),
            )
        else:
            user_row = conn.execute("SELECT password_hash FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if not user_row:
                raise ValueError("User not found.")
            if not verify_password(current_password, user_row["password_hash"]):
                raise ValueError("Current password is incorrect.")
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE user_id = ?",
                (hash_password(new_password), user_id),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_settings(user_id: str, company_id: str) -> Dict[str, Any]:
    conn = _connect()
    try:
        if is_postgres_enabled():
            row = conn.execute(
                "SELECT * FROM user_settings WHERE user_id = %s AND company_id = %s",
                (user_id, company_id),
            ).fetchone()
            if row:
                return {
                    "preferences": row["preferences"] or {},
                    "dashboard_settings": row["dashboard_settings"] or {},
                    "updated_at": row["updated_at"],
                }
            return {"preferences": {}, "dashboard_settings": {}}

        row = conn.execute(
            "SELECT * FROM user_settings WHERE user_id = ? AND company_id = ?",
            (user_id, company_id),
        ).fetchone()
        if row:
            import json
            return {
                "preferences": json.loads(row["preferences"] or '{}'),
                "dashboard_settings": json.loads(row["dashboard_settings"] or '{}'),
                "updated_at": row["updated_at"],
            }
        return {"preferences": {}, "dashboard_settings": {}}
    finally:
        conn.close()


def save_user_settings(user_id: str, company_id: str, preferences: Optional[Dict[str, Any]] = None, dashboard_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if preferences is None:
        preferences = {}
    if dashboard_settings is None:
        dashboard_settings = {}

    conn = _connect()
    try:
        now = _iso(_now_utc())
        if is_postgres_enabled():
            row = conn.execute(
                "SELECT setting_id FROM user_settings WHERE user_id = %s AND company_id = %s",
                (user_id, company_id),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE user_settings SET preferences = %s, dashboard_settings = %s, updated_at = NOW() WHERE setting_id = %s",
                    (preferences, dashboard_settings, row["setting_id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO user_settings (setting_id, user_id, company_id, preferences, dashboard_settings, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                    (_setting_id(), user_id, company_id, preferences, dashboard_settings),
                )
        else:
            import json
            row = conn.execute(
                "SELECT setting_id FROM user_settings WHERE user_id = ? AND company_id = ?",
                (user_id, company_id),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE user_settings SET preferences = ?, dashboard_settings = ?, updated_at = ? WHERE setting_id = ?",
                    (json.dumps(preferences), json.dumps(dashboard_settings), now, row["setting_id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO user_settings (setting_id, user_id, company_id, preferences, dashboard_settings, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (_setting_id(), user_id, company_id, json.dumps(preferences), json.dumps(dashboard_settings), now, now),
                )
        conn.commit()
        return {"preferences": preferences, "dashboard_settings": dashboard_settings}
    finally:
        conn.close()


init_auth_db()
