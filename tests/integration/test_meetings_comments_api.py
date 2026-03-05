import pytest

from app.db import get_database


@pytest.fixture(autouse=True)
def clear_comments(client):
    db = get_database(client.application)
    db.comments.delete_many({})
    yield
    db.comments.delete_many({})


@pytest.fixture(autouse=True)
def bypass_guard(monkeypatch):
    monkeypatch.setattr("app.middleware.auth_guard._is_valid_access_token", lambda _token: True)
    yield


def _auth_headers(token: str = "test-token"):
    return {"Authorization": f"Bearer {token}"}


def _create_meeting(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    payload = {
        "title": "댓글 테스트 모임",
        "place": "장소",
        "scheduled_at": "2030-06-01T12:00:00+09:00",
        "max_capacity": 4,
    }
    res = client.post("/api/v1/meetings", json=payload, headers=_auth_headers())
    return res.get_json()["data"]["meeting_id"]


@pytest.mark.integration
def test_create_comment_success(client):
    meeting_id = _create_meeting(client)
    payload = {"body": "첫 댓글입니다."}
    response = client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json=payload,
        headers=_auth_headers(),
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["body"] == "첫 댓글입니다."
    assert body["data"]["meeting_id"] == meeting_id
    assert "comment_id" in body["data"]
    assert "author_nickname" in body["data"]


@pytest.mark.integration
def test_list_comments_success(client):
    meeting_id = _create_meeting(client)
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "댓글1"},
        headers=_auth_headers(),
    )
    client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "댓글2"},
        headers=_auth_headers(),
    )
    response = client.get(f"/api/v1/meetings/{meeting_id}/comments")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]["items"]) == 2
    texts = [it["body"] for it in body["data"]["items"]]
    assert "댓글1" in texts
    assert "댓글2" in texts


@pytest.mark.integration
def test_delete_comment_success(client):
    meeting_id = _create_meeting(client)
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    create_res = client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "삭제할 댓글"},
        headers=_auth_headers(),
    )
    comment_id = create_res.get_json()["data"]["comment_id"]
    response = client.delete(
        f"/api/v1/meetings/{meeting_id}/comments/{comment_id}",
        headers=_auth_headers(),
    )
    assert response.status_code == 204
    list_res = client.get(f"/api/v1/meetings/{meeting_id}/comments")
    assert len(list_res.get_json()["data"]["items"]) == 0


@pytest.mark.integration
def test_delete_comment_forbidden_if_not_author(client):
    meeting_id = _create_meeting(client)
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    create_res = client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "다른 사람 댓글"},
        headers=_auth_headers("user1-token"),
    )
    comment_id = create_res.get_json()["data"]["comment_id"]
    with client.session_transaction() as sess:
        sess["user_id"] = "user2"
    response = client.delete(
        f"/api/v1/meetings/{meeting_id}/comments/{comment_id}",
        headers=_auth_headers("user2-token"),
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_create_reply_and_list_nested(client):
    meeting_id = _create_meeting(client)
    with client.session_transaction() as sess:
        sess["user_id"] = "user1"
    parent_res = client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "부모 댓글"},
        headers=_auth_headers(),
    )
    parent_id = parent_res.get_json()["data"]["comment_id"]
    reply_res = client.post(
        f"/api/v1/meetings/{meeting_id}/comments",
        json={"body": "대댓글", "parent_id": parent_id},
        headers=_auth_headers(),
    )
    assert reply_res.status_code == 201
    assert reply_res.get_json()["data"].get("parent_id") == parent_id

    list_res = client.get(f"/api/v1/meetings/{meeting_id}/comments")
    assert list_res.status_code == 200
    items = list_res.get_json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["body"] == "부모 댓글"
    assert "replies" in items[0]
    assert len(items[0]["replies"]) == 1
    assert items[0]["replies"][0]["body"] == "대댓글"
