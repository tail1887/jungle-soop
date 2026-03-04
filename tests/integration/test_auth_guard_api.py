import pytest
from app.db import get_database
from app.utils.security import hash_password

@pytest.mark.integration
def test_guard_blocks_unauthorized_request(client):
    """[401 테스트] 인증 없이 보호된 API 요청 시 차단 검증"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.integration
def test_auth_guard_success_with_valid_token(client):
    """[성공 테스트] 유효한 토큰으로 인증 통과 및 로그아웃 성공 검증"""
    email = "guard-success@jungle.soop"
    password = "password1234"
    
    # 테스트 유저 준비
    db = get_database(client.application)
    db.users.delete_one({"email": email})
    db.users.insert_one({
        "email": email,
        "password_hash": hash_password(password),
        "nickname": "가드성공"
    })

    # 로그인 및 토큰 추출
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    login_data = login_res.get_json()
    
    token = None
    if login_data.get("success"):
        token = login_data.get("access_token") or login_data.get("data", {}).get("access_token")
    
    if not token:
        pytest.fail(f"로그인 실패 또는 토큰 누락. 응답: {login_data}")

    # 인증된 요청 발송
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.get_json()["success"] is True

@pytest.mark.integration
def test_guard_blocks_forbidden_resource_access(client):
    """[403 테스트] 타인의 리소스 접근 시 403 Forbidden 차단 검증"""
    db = get_database(client.application)
    db.users.delete_many({"email": {"$in": ["owner@jungle.soop", "attacker@jungle.soop"]}})
    
    # 1. 자원 소유자(Owner)와 침입자(Attacker) 생성
    owner_id = db.users.insert_one({
        "email": "owner@jungle.soop",
        "password_hash": hash_password("pass"),
        "nickname": "주인"
    }).inserted_id
    
    db.users.insert_one({
        "email": "attacker@jungle.soop",
        "password_hash": hash_password("pass"),
        "nickname": "침입자"
    })

    # 2. 침입자로 로그인하여 토큰