import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-join 구현 후 활성화")
def test_join_meeting_success(client):
    # TODO: 참여 성공(200) 검증
    response = client.post("/api/v1/meetings/sample/join")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-join 구현 후 활성화")
def test_cancel_join_meeting_success(client):
    # TODO: 참여 취소 성공(200) 검증
    response = client.delete("/api/v1/meetings/sample/join")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-join 구현 후 활성화")
def test_join_meeting_conflict_when_full(client):
    # TODO: 정원 초과 시 409 + 공통 실패 포맷 검증
    response = client.post("/api/v1/meetings/sample/join")
    assert response.status_code == 409
