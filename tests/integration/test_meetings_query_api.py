import pytest

from app.db import get_database


@pytest.fixture(autouse=True)
def clear_meetings(client):
    db = get_database(client.application)
    db.meetings.delete_many({})
    yield
    db.meetings.delete_many({})


@pytest.fixture(autouse=True)
def bypass_guard(monkeypatch):
    monkeypatch.setattr(
        "app.middleware.auth_guard._is_valid_access_token", lambda _token: True
    )
    yield


def _auth_headers(token: str = "test-token"):
    return {"Authorization": f"Bearer {token}"}


def _create_meeting(client, user_id: str, title: str, scheduled_at: str):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    payload = {
        "title": title,
        "description": "설명",
        "place": "기숙사",
        "scheduled_at": scheduled_at,
        "max_capacity": 4,
    }
    response = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    return response.get_json()["data"]["meeting_id"]


@pytest.mark.integration
def test_list_meetings_success(client):
    _create_meeting(client, "user1", "모임1", "2026-03-05T18:30:00+09:00")
    _create_meeting(client, "user2", "모임2", "2026-03-04T18:30:00+09:00")
    _create_meeting(client, "user3", "모임3", "2026-03-03T18:30:00+09:00")

    response = client.get("/api/v1/meetings?sort=deadline&page=1&limit=2")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "pagination" in body["data"]
    assert len(body["data"]["items"]) == 2
    assert body["data"]["pagination"]["page"] == 1
    assert body["data"]["pagination"]["limit"] == 2
    assert body["data"]["pagination"]["total"] == 3
    assert body["data"]["pagination"]["total_pages"] == 2

    # deadline 정렬은 scheduled_at 오름차순
    first, second = body["data"]["items"][0], body["data"]["items"][1]
    assert first["scheduled_at"] <= second["scheduled_at"]
    assert "meeting_id" in first
    assert "participant_count" in first


@pytest.mark.integration
def test_get_meeting_detail_success(client):
    meeting_id = _create_meeting(
        client,
        "user1",
        "상세 테스트 모임",
        "2026-04-01T12:00:00+09:00",
    )

    response = client.get(f"/api/v1/meetings/{meeting_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["meeting_id"] == meeting_id
    assert body["data"]["title"] == "상세 테스트 모임"
    assert body["data"]["participant_count"] == 1
    assert body["data"]["participants"] == ["user1"]


@pytest.mark.integration
def test_get_meeting_detail_not_found(client):
    response = client.get("/api/v1/meetings/000000000000000000000000")
    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "MEETING_NOT_FOUND"
