import pytest
from app.db import get_database
from app.utils.security import hash_password

@pytest.mark.integration
def test_login_success(client):
    email = "test@jungle.soop"
    password = "password1234"
    
    db = get_database(client.application)
    hashed = hash_password(password)
    user_data = {
        "email": email,
        "password_hash": hashed,
        "nickname": "테스터"
    }

    # 1. 의심되는 모든 컬렉션에서 기존 유저 삭제 및 새로 삽입
    for col in ["user", "users", "member", "members"]:
        db[col].delete_one({"email": email})
        db[col].insert_one(user_data.copy())

    # 2. 로그인 요청
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    
    # 3. 실패 시 서버가 DB에서 무엇을 조회했는지 print로 확인 (UserRepository 내부 로직 확인용)
    if response.status_code != 200:
        print(f"\n[실패 응답 데이터]: {response.get_json()}")

    assert response.status_code == 200