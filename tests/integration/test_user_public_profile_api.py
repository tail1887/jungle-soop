import pytest
from bson import ObjectId

from app.db import get_database


@pytest.mark.integration
def test_get_public_user_profile_api_returns_email_and_nickname(app, client):
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
        resp = client.get(f"/api/v1/users/{user_id}")
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
    # 잘못된 ObjectId 형식이면 404
    resp = client.get("/api/v1/users/not-an-objectid")
    assert resp.status_code == 404


@pytest.mark.integration
def test_get_public_user_profile_api_not_found_returns_404(client):
    # 형식은 맞지만 없는 유저여도 404
    non_existent_id = "64b7cbf0f1a2b3c4d5e6f7a8"
    resp = client.get(f"/api/v1/users/{non_existent_id}")
    assert resp.status_code == 404