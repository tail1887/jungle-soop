import pytest

from app.db import get_database


@pytest.fixture(autouse=True)
def clear_users(client):
    db = get_database(client.application)
    db.users.delete_many({})
    yield
    db.users.delete_many({})


def _signup_payload(email: str) -> dict:
    return {
        "email": email,
        "password": "password123",
        "nickname": "정글러",
    }


@pytest.mark.integration
def test_signup_success(client):
    response = client.post("/api/v1/auth/signup", json=_signup_payload("signup_ok@jungle.com"))

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert "user_id" in body["data"]


@pytest.mark.integration
def test_signup_duplicate_email(client):
    email = "signup_dup@jungle.com"
    first = client.post("/api/v1/auth/signup", json=_signup_payload(email))
    assert first.status_code == 201

    second = client.post("/api/v1/auth/signup", json=_signup_payload(email))
    assert second.status_code == 409
    body = second.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.integration
def test_signup_invalid_input(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "invalid_input@jungle.com", "nickname": "정글러"},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_INPUT"
