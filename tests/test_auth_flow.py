import os
import sqlite3

from fastapi.testclient import TestClient

from api.server import app


def reset_auth_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "auth.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM sessions")
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM companies")
        conn.commit()
        conn.close()


def test_register_and_login_success():
    reset_auth_db()
    client = TestClient(app)

    register_response = client.post(
        "/auth/register",
        json={
            "company_name": "Acme Analytics",
            "full_name": "Jane Manager",
            "email": "jane@acme.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
        },
    )

    assert register_response.status_code == 200, register_response.text
    payload = register_response.json()
    assert payload["company_id"].startswith("CMP-")
    assert payload["user_id"].startswith("USR-")

    login_response = client.post(
        "/auth/login",
        json={"email": "jane@acme.com", "password": "StrongPass!123"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["token"]
    assert token

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200, me_response.text
    me = me_response.json()
    assert me["company_id"] == payload["company_id"]
    assert me["email"] == "jane@acme.com"


def test_duplicate_registration_and_invalid_login_are_rejected():
    reset_auth_db()
    client = TestClient(app)

    first = client.post(
        "/auth/register",
        json={
            "company_name": "Alpha Labs",
            "full_name": "Alex Admin",
            "email": "alex@alpha.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
        },
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/auth/register",
        json={
            "company_name": "Alpha Labs",
            "full_name": "Another User",
            "email": "another@alpha.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
        },
    )
    assert duplicate.status_code == 409

    bad_login = client.post(
        "/auth/login",
        json={"email": "alex@alpha.com", "password": "wrongpass"},
    )
    assert bad_login.status_code == 401


def test_company_isolation_is_enforced_for_session_auth():
    reset_auth_db()
    client = TestClient(app)

    first = client.post(
        "/auth/register",
        json={
            "company_name": "Company A",
            "full_name": "A Admin",
            "email": "admin@companya.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
        },
    )
    second = client.post(
        "/auth/register",
        json={
            "company_name": "Company B",
            "full_name": "B Admin",
            "email": "admin@companyb.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    token_a = client.post(
        "/auth/login",
        json={"email": "admin@companya.com", "password": "StrongPass!123"},
    ).json()["token"]
    token_b = client.post(
        "/auth/login",
        json={"email": "admin@companyb.com", "password": "StrongPass!123"},
    ).json()["token"]

    res_a = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    res_b = client.get("/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.json()["company_id"] != res_b.json()["company_id"]
