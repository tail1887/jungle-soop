import pytest
from bson import ObjectId
import uuid

from app.db import get_database


def _signup_and_login(client):
    email = f"user-profile-{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "email": email,
        "password": "password123",
        "nickname": "viewer",
    }
    signup_resp = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": signup_payload["email"], "password": signup_payload["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_get_public_user_profile_api_returns_email_and_nickname(app, client):
    headers = _signup_and_login(client)

    # given: 테스트용 유저 한 명을 DB에 삽입
    db = get_database(app)
    users = db.users
    user_doc = {
        "_id": ObjectId(),
        "email": "test-user@example.com",
        "nickname": "테스트유저",
        "password": "hashed-password-should-not-leak",
    }
    users.insert_one(user_doc)

    try:
        # when: 공개 프로필 API를 호출
        user_id = str(user_doc["_id"])
        resp = client.get(f"/api/v1/users/{user_id}", headers=headers)
        data = resp.get_json()

        # then: 상태코드 및 응답 내용 검증
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["data"]["user_id"] == user_id
        assert data["data"]["email"] == user_doc["email"]
        assert data["data"]["nickname"] == user_doc["nickname"]
        # password 같은 민감 정보는 포함되지 않아야 함
        assert "password" not in data["data"]
    finally:
        # 정리: 테스트 데이터 삭제
        users.delete_one({"_id": user_doc["_id"]})


@pytest.mark.integration
def test_get_public_user_profile_api_invalid_id_returns_404(client):
    headers = _signup_and_login(client)

    # 잘못된 ObjectId 형식이면 404
    resp = client.get("/api/v1/users/not-an-objectid", headers=headers)
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.integration
def test_get_public_user_profile_api_not_found_returns_404(client):
    headers = _signup_and_login(client)

    # 형식은 맞지만 없는 유저여도 404
    non_existent_id = "64b7cbf0f1a2b3c4d5e6f7a8"
    resp = client.get(f"/api/v1/users/{non_existent_id}", headers=headers)
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.integration
def test_get_public_user_profile_api_requires_auth(client):
    db = get_database(client.application)
    users = db.users
    user_doc = {
        "_id": ObjectId(),
        "email": "protected-user@example.com",
        "nickname": "protected",
        "password_hash": "dummy",
    }
    users.insert_one(user_doc)
    try:
        resp = client.get(f"/api/v1/users/{str(user_doc['_id'])}")
        assert resp.status_code == 401
        body = resp.get_json()
        assert body["success"] is False
        assert body["error"]["code"] == "UNAUTHORIZED"
    finally:
        users.delete_one({"_id": user_doc["_id"]})