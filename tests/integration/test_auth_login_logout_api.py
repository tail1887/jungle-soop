import pytest

from app.db import get_database
from app.utils.security import hash_password


@pytest.fixture(autouse=True)
def clear_users(client):
    db = get_database(client.application)
    db.users.delete_many({})
    yield
    db.users.delete_many({})


@pytest.mark.integration
def test_login_success(client):
    email = "test@jungle.soop"
    password = "password1234"

    db = get_database(client.application)
    hashed = hash_password(password)
    db.users.insert_one(
        {
        "email": email,
        "password_hash": hashed,
            "nickname": "테스터",
        }
    )

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["nickname"] == "테스터"
    assert body["data"]["access_token"]


@pytest.mark.integration
def test_login_fails_with_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nouser@jungle.soop", "password": "wrong-password"},
    )
    assert response.status_code == 401
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.integration
def test_login_fails_with_missing_input(client):
    response = client.post("/api/v1/auth/login", json={"email": "only-email@jungle.soop"})
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_INPUT"


@pytest.mark.integration
def test_logout_success(client):
    email = "logout-test@jungle.soop"
    password = "password1234"

    db = get_database(client.application)
    db.users.insert_one(
        {
            "email": email,
            "password_hash": hash_password(password),
            "nickname": "로그아웃테스터",
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["data"]["access_token"]

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True