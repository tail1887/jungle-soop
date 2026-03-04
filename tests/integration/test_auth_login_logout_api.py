import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/auth-login-logout 구현 후 활성화")
def test_login_success(client):
    # TODO: 로그인 성공(200) + 세션 생성 여부 검증
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/auth-login-logout 구현 후 활성화")
def test_logout_success(client):
    # TODO: 로그아웃 성공(200) + 세션 삭제 여부 검증
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
