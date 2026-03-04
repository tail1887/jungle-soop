import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-query 구현 후 활성화")
def test_list_meetings_success(client):
    # TODO: 목록 조회(200) + pagination/filter 응답 검증
    response = client.get("/api/v1/meetings")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="handcoding template: feature/meetings-query 구현 후 활성화")
def test_get_meeting_detail_success(client):
    # TODO: 상세 조회(200) 검증
    response = client.get("/api/v1/meetings/sample")
    assert response.status_code == 200
