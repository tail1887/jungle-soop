import pytest
from flask import jsonify

from app.db import get_database
from app.middleware.auth_guard import check_ownership, login_required
from app.utils.security import hash_password


@pytest.fixture(autouse=True)
def clear_users(client):
    db = get_database(client.application)
    db.users.delete_many({})
    yield
    db.users.delete_many({})


@pytest.fixture(autouse=True)
def register_permission_test_route(client):
    app = client.application
    endpoint = "__auth_guard_permission_test__"
    if endpoint not in app.view_functions:

        @login_required
        def _permission_probe(owner_id: str):
            error_response = check_ownership(owner_id)
            if error_response:
                return error_response
            return jsonify({"success": True, "data": {"owner_id": owner_id}}), 200

        app.add_url_rule(
            "/_test/auth/permission/<owner_id>",
            endpoint,
            _permission_probe,
            methods=["DELETE"],
        )
    yield


@pytest.mark.integration
def test_guard_blocks_unauthorized_request(client):
    """인증 없이 보호 API 요청 시 401 반환"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.integration
def test_auth_guard_success_with_valid_token(client):
    """유효한 토큰이면 인증 통과"""
    email = "guard-success@jungle.soop"
    password = "password1234"

    db = get_database(client.application)
    db.users.insert_one(
        {
            "email": email,
            "password_hash": hash_password(password),
            "nickname": "가드성공",
        }
    )

    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    login_data = login_res.get_json()
    token = login_data.get("data", {}).get("access_token")
    if not token:
        pytest.fail(f"로그인 실패 또는 토큰 누락. 응답: {login_data}")

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["success"] is True


@pytest.mark.integration
def test_guard_blocks_forbidden_resource_access(client):
    """타인의 리소스 접근 시 403 반환"""
    db = get_database(client.application)
    owner_id = db.users.insert_one(
        {
            "email": "owner@jungle.soop",
            "password_hash": hash_password("pass"),
            "nickname": "주인",
        }
    ).inserted_id
    db.users.insert_one(
        {
            "email": "attacker@jungle.soop",
            "password_hash": hash_password("pass"),
            "nickname": "침입자",
        }
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "attacker@jungle.soop", "password": "pass"},
    )
    token = login_res.get_json().get("data", {}).get("access_token")
    assert token

    response = client.delete(
        f"/_test/auth/permission/{owner_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"