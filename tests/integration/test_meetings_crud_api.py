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
    # JWT guard 미구현 구간을 우회해 CRUD 비즈니스 로직을 검증합니다.
    monkeypatch.setattr("app.middleware.auth_guard._is_valid_access_token", lambda _token: True)
    yield


def _auth_headers(token: str = "test-token"):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_create_meeting_success(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    payload = {
        "title": "저녁 같이 먹을 사람",
        "description": "분식집 가실 분 구해요.",
        "place": "기숙사 정문",
        "scheduled_at": "2026-03-05T18:30:00+09:00",
        "max_capacity": 4,
    }
    response = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert "meeting_id" in body["data"]


@pytest.mark.integration
def test_update_meeting_success(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    payload = {
        "title": "모임 제목",
        "place": "장소",
        "scheduled_at": "2026-04-01T12:00:00+09:00",
        "max_capacity": 5,
    }
    create_res = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    meeting_id = create_res.get_json()["data"]["meeting_id"]

    patch_payload = {"title": "모임 제목(수정)", "scheduled_at": "2026-04-01T13:00:00+09:00"}
    response = client.patch(
        f"/api/v1/meetings/{meeting_id}",
        json=patch_payload,
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["meeting_id"] == meeting_id


@pytest.mark.integration
def test_delete_meeting_success(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    payload = {
        "title": "삭제할 모임",
        "place": "어디",
        "scheduled_at": "2026-05-01T12:00:00+09:00",
        "max_capacity": 10,
    }
    create_res = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    meeting_id = create_res.get_json()["data"]["meeting_id"]

    response = client.delete(f"/api/v1/meetings/{meeting_id}", headers=_auth_headers())
    assert response.status_code == 204
    assert response.data == b""


@pytest.mark.integration
def test_update_forbidden_if_not_author(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    payload = {
        "title": "비밀 모임",
        "place": "장소",
        "scheduled_at": "2026-06-01T12:00:00+09:00",
        "max_capacity": 5,
    }
    create_res = client.post("/api/v1/meetings", json=payload, headers=_auth_headers("author-token"))
    meeting_id = create_res.get_json()["data"]["meeting_id"]

    with client.session_transaction() as sess:
        sess["user_id"] = "other"

    response = client.patch(
        f"/api/v1/meetings/{meeting_id}",
        json={"title": "hack"},
        headers=_auth_headers("other-token"),
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_delete_forbidden_if_not_author(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"

    payload = {
        "title": "삭제 못해",
        "place": "어디",
        "scheduled_at": "2026-07-01T12:00:00+09:00",
        "max_capacity": 5,
    }
    create_res = client.post("/api/v1/meetings", json=payload, headers=_auth_headers("author-token"))
    meeting_id = create_res.get_json()["data"]["meeting_id"]

    with client.session_transaction() as sess:
        sess["user_id"] = "other"

    response = client.delete(
        f"/api/v1/meetings/{meeting_id}",
        headers=_auth_headers("other-token"),
    )
    assert response.status_code == 403
