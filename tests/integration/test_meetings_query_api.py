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


def _create_meeting(client, user_id: str, title: str, scheduled_at: str, category: str = "other"):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    payload = {
        "title": title,
        "description": "설명",
        "place": "기숙사",
        "scheduled_at": scheduled_at,
        "max_capacity": 4,
        "category": category,
    }
    response = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    return response.get_json()["data"]["meeting_id"]


@pytest.mark.integration
def test_list_meetings_success(client):
    _create_meeting(client, "user1", "모임1", "2030-03-05T18:30:00+09:00")
    _create_meeting(client, "user2", "모임2", "2030-03-04T18:30:00+09:00")
    _create_meeting(client, "user3", "모임3", "2030-03-03T18:30:00+09:00")

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
    assert "deadline_at" in first


@pytest.mark.integration
def test_get_meeting_detail_success(client):
    meeting_id = _create_meeting(
        client,
        "user1",
        "상세 테스트 모임",
        "2030-04-01T12:00:00+09:00",
    )

    response = client.get(f"/api/v1/meetings/{meeting_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["meeting_id"] == meeting_id
    assert body["data"]["title"] == "상세 테스트 모임"
    assert body["data"]["participant_count"] == 1
    assert len(body["data"]["participants"]) == 1
    assert body["data"]["participants"][0]["user_id"] == "user1"
    assert "nickname" in body["data"]["participants"][0]
    assert body["data"]["deadline_at"] == body["data"]["scheduled_at"]


@pytest.mark.integration
def test_list_meetings_deadline_sort_uses_deadline_at(client):
    _create_meeting(
        client,
        "user1",
        "마감 늦은 모임",
        "2030-04-10T12:00:00+09:00",
    )

    with client.session_transaction() as sess:
        sess["user_id"] = "user2"
    client.post(
        "/api/v1/meetings",
        json={
            "title": "마감 빠른 모임",
            "description": "설명",
            "place": "기숙사",
            "scheduled_at": "2030-04-20T12:00:00+09:00",
            "deadline_at": "2030-04-01T12:00:00+09:00",
            "max_capacity": 4,
        },
        headers=_auth_headers(),
    )

    response = client.get("/api/v1/meetings?sort=deadline&page=1&limit=10")
    assert response.status_code == 200
    items = response.get_json()["data"]["items"]
    assert len(items) >= 2
    assert items[0]["title"] == "마감 빠른 모임"
    assert items[0]["deadline_at"] == "2030-04-01T12:00:00+09:00"


@pytest.mark.integration
def test_get_meeting_detail_not_found(client):
    response = client.get("/api/v1/meetings/000000000000000000000000")
    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "MEETING_NOT_FOUND"


@pytest.mark.integration
def test_list_meetings_filter_by_title_search(client):
    _create_meeting(client, "user1", "저녁 같이 먹을 사람", "2030-03-05T18:30:00+09:00")
    _create_meeting(client, "user2", "점심 런치 모임", "2030-03-04T18:30:00+09:00")
    _create_meeting(client, "user3", "저녁 회의", "2030-03-03T18:30:00+09:00")

    response = client.get("/api/v1/meetings?q=저녁")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    items = body["data"]["items"]
    assert len(items) == 2
    titles = [it["title"] for it in items]
    assert "저녁 같이 먹을 사람" in titles
    assert "저녁 회의" in titles
    assert "점심 런치 모임" not in titles

    response_empty = client.get("/api/v1/meetings?q=없는검색어")
    assert response_empty.status_code == 200
    assert len(response_empty.get_json()["data"]["items"]) == 0


@pytest.mark.integration
def test_list_meetings_filter_by_category(client):
    _create_meeting(client, "user1", "식사 모임", "2030-03-05T18:30:00+09:00", "meal")
    _create_meeting(client, "user2", "운동 모임", "2030-03-04T18:30:00+09:00", "exercise")
    _create_meeting(client, "user3", "스터디 모임", "2030-03-03T18:30:00+09:00", "study")

    response = client.get("/api/v1/meetings?category=meal")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    items = body["data"]["items"]
    assert len(items) == 1
    assert items[0]["title"] == "식사 모임"
    assert items[0]["category"] == "meal"

    response_all = client.get("/api/v1/meetings")
    assert response_all.status_code == 200
    assert len(response_all.get_json()["data"]["items"]) >= 3
