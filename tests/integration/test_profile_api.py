import pytest

def get_auth_headers(client):
    """테스트용 계정으로 로그인하여 토큰 헤더를 생성하는 함수"""
    # 1. 테스트용 계정 생성 (이미 있으면 에러나겠지만 무시)
    client.post("/api/v1/auth/signup", json={
        "email": "test_user@example.com",
        "password": "password123",
        "nickname": "초기닉네임"
    })
    
    # 2. 로그인하여 토큰 받기
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test_user@example.com",
        "password": "password123"
    })
    token = login_res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_profile_api_flow(client):
    """[통합 테스트] 조회 -> 수정 -> 재조회 흐름 확인"""
    # 0. 로그인 헤더 준비
    headers = get_auth_headers(client)
    
    # 1. 초기 조회 (GET)
    get_res = client.get("/api/v1/profile/me", headers=headers)
    assert get_res.status_code == 200
    
    # 2. 닉네임 수정 (PATCH)
    new_name = "정글왕은열"
    patch_res = client.patch(
        "/api/v1/profile/me",
        json={"nickname": new_name},
        headers=headers
    )
    assert patch_res.status_code == 200
    assert patch_res.get_json()["data"]["nickname"] == new_name
    
    # 3. 수정 후 재조회 일관성 확인 (GET)
    final_res = client.get("/api/v1/profile/me", headers=headers)
    assert final_res.get_json()["data"]["nickname"] == new_name
    assert final_res.get_json()["success"] is True

def test_get_profile_unauthorized(client):
    """[예외] 토큰 없이 접근 시 401 확인"""
    response = client.get("/api/v1/profile/me")
    assert response.status_code == 401