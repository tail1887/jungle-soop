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


def _create_meeting(client, user_id: str, payload: dict):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    return response.get_json()["data"]["meeting_id"]


@pytest.mark.integration
def test_join_meeting_success(client):
    meeting_id = _create_meeting(
        client,
        "author1",
        {
            "title": "참여 테스트 모임",
            "description": "설명",
            "place": "기숙사",
            "scheduled_at": "2026-08-01T12:00:00+09:00",
            "max_capacity": 3,
        },
    )

    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    response = client.post(f"/api/v1/meetings/{meeting_id}/join", headers=_auth_headers())
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["meeting_id"] == meeting_id
    assert body["data"]["participant_count"] == 2
    assert body["data"]["status"] == "open"


@pytest.mark.integration
def test_cancel_join_meeting_success(client):
    meeting_id = _create_meeting(
        client,
        "author1",
        {
            "title": "취소 테스트 모임",
            "description": "설명",
            "place": "기숙사",
            "scheduled_at": "2026-08-02T12:00:00+09:00",
            "max_capacity": 3,
        },
    )

    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    join_res = client.post(f"/api/v1/meetings/{meeting_id}/join", headers=_auth_headers())
    assert join_res.status_code == 200

    response = client.delete(f"/api/v1/meetings/{meeting_id}/join", headers=_auth_headers())
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["meeting_id"] == meeting_id
    assert body["data"]["participant_count"] == 1


@pytest.mark.integration
def test_join_meeting_conflict_when_full(client):
    meeting_id = _create_meeting(
        client,
        "author1",
        {
            "title": "정원 테스트 모임",
            "description": "설명",
            "place": "기숙사",
            "scheduled_at": "2026-08-03T12:00:00+09:00",
            "max_capacity": 2,
        },
    )

    with client.session_transaction() as sess:
        sess["user_id"] = "user2"
    first_join = client.post(f"/api/v1/meetings/{meeting_id}/join", headers=_auth_headers())
    assert first_join.status_code == 200

    with client.session_transaction() as sess:
        sess["user_id"] = "user3"
    response = client.post(f"/api/v1/meetings/{meeting_id}/join", headers=_auth_headers())
    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "MEETING_FULL"
