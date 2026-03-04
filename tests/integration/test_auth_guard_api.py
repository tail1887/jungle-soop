import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/auth-guard 구현 후 활성화")
def test_guard_blocks_unauthorized_request(client):
    # TODO: 보호 API 요청 시 401/공통 실패 포맷 검증
    response = client.post("/api/v1/meetings/sample/join")
    assert response.status_code == 401
