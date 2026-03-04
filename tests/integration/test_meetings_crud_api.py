import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-crud 구현 후 활성화")
def test_create_meeting_success(client):
    # TODO: 모임 생성(201) 검증
    response = client.post("/api/v1/meetings", json={})
    assert response.status_code == 201


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-crud 구현 후 활성화")
def test_update_meeting_success(client):
    # TODO: 모임 수정(200) 검증
    response = client.patch("/api/v1/meetings/sample", json={})
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-crud 구현 후 활성화")
def test_delete_meeting_success(client):
    # TODO: 모임 삭제(200 또는 204) 검증
    response = client.delete("/api/v1/meetings/sample")
    assert response.status_code in (200, 204)
