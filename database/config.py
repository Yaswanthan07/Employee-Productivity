import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/auth.db")
APP_ENV = os.getenv("APP_ENV", "development")


def get_database_url() -> str:
    return DATABASE_URL


def is_postgres_enabled() -> bool:
    return DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres://")
