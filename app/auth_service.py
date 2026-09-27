import os
import re
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import bcrypt

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "auth.db"


def _connect() -> sqlite3.Connection:
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_auth_db() -> None:
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            company_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
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
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
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
    conn.commit()
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
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


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
        conn.execute("BEGIN IMMEDIATE")

        existing_company = conn.execute(
            "SELECT company_id FROM companies WHERE company_name = ? COLLATE NOCASE",
            (company_name.strip(),),
        ).fetchone()
        if existing_company:
            raise ValueError("A company with this name is already registered.")

        existing_user = conn.execute(
            "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
            (normalized_email,),
        ).fetchone()
        if existing_user:
            raise ValueError("An account with this email already exists.")

        company_id = _company_id()
        user_id = _user_id()
        now = _iso(_now_utc())
        company_hash = hash_password(password)

        conn.execute(
            "INSERT INTO companies (company_id, company_name, status, created_at) VALUES (?, ?, 'active', ?)",
            (company_id, company_name.strip(), now),
        )
        conn.execute(
            "INSERT INTO users (user_id, company_id, full_name, email, password_hash, role, status, created_at) VALUES (?, ?, ?, ?, ?, 'HR', 'active', ?)",
            (user_id, company_id, full_name.strip(), normalized_email, company_hash, now),
        )
        conn.commit()
        return {
            "company_id": company_id,
            "user_id": user_id,
            "company_name": company_name.strip(),
            "email": normalized_email,
        }
    except Exception:
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
        user_row = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE AND status = 'active'",
            (normalized_email,),
        ).fetchone()
        if not user_row:
            raise ValueError("Invalid email or password.")

        if not verify_password(password, user_row["password_hash"]):
            raise ValueError("Invalid email or password.")

        token = _session_id()
        expires_at = _iso(_now_utc() + timedelta(days=7))
        now = _iso(_now_utc())
        conn.execute(
            "INSERT INTO sessions (session_id, user_id, company_id, expires_at, revoked, created_at) VALUES (?, ?, ?, ?, 0, ?)",
            (token, user_row["user_id"], user_row["company_id"], expires_at, now),
        )
        conn.commit()

        company_row = conn.execute(
            "SELECT company_name FROM companies WHERE company_id = ?",
            (user_row["company_id"],),
        ).fetchone()

        return {
            "token": token,
            "user_id": user_row["user_id"],
            "company_id": user_row["company_id"],
            "company_name": company_row["company_name"] if company_row else "Company",
            "full_name": user_row["full_name"],
            "email": user_row["email"],
            "role": user_row["role"],
            "expires_at": expires_at,
        }
    finally:
        conn.close()


def get_session_context(session_token: str) -> Optional[Dict[str, Any]]:
    if not session_token:
        return None

    init_auth_db()
    conn = _connect()
    try:
        now = _now_utc()
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

        expires_at = datetime.fromisoformat(row["expires_at"]).astimezone(timezone.utc)
        if expires_at <= now:
            conn.execute("UPDATE sessions SET revoked = 1 WHERE session_id = ?", (session_token,))
            conn.commit()
            return None

        return {
            "session_id": row["session_id"],
            "user_id": row["user_id"],
            "company_id": row["company_id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": row["role"],
        }
    finally:
        conn.close()


def logout_session(session_token: str) -> bool:
    if not session_token:
        return False

    conn = _connect()
    try:
        result = conn.execute(
            "UPDATE sessions SET revoked = 1 WHERE session_id = ? AND revoked = 0",
            (session_token,),
        )
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT u.user_id, u.company_id, u.full_name, u.email, u.role, u.status, u.created_at,
                   c.company_name
            FROM users u
            INNER JOIN companies c ON c.company_id = u.company_id
            WHERE u.user_id = ?
            """,
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "user_id": row["user_id"],
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": row["role"],
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


init_auth_db()
