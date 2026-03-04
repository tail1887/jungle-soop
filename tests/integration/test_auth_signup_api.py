import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/auth-signup 구현 후 활성화")
def test_signup_success(client):
    # TODO: 성공 케이스(201) + success/data 검증
    response = client.post("/api/v1/auth/signup", json={})
    assert response.status_code == 201


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/auth-signup 구현 후 활성화")
def test_signup_duplicate_email(client):
    # TODO: 중복 이메일 케이스(409) + EMAIL_ALREADY_EXISTS 검증
    response = client.post("/api/v1/auth/signup", json={})
    assert response.status_code == 409
