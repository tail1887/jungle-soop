import uuid

import pytest
from flask import current_app

from app.db import get_database


@pytest.fixture(autouse=True)
def clear_profile_collections(client):
    db = get_database(client.application)
    db.users.delete_many({})
    db.meetings.delete_many({})
    yield
    db.users.delete_many({})
    db.meetings.delete_many({})


def _signup_and_login(client):
    suffix = uuid.uuid4().hex[:8]
    email = f"profile_{suffix}@example.com"
    password = "password123"
    nickname = f"user_{suffix}"

    signup_res = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "nickname": nickname},
    )
    assert signup_res.status_code == 201

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200

    body = login_res.get_json()
    user_id = body["data"]["user_id"]
    token = body["data"]["access_token"]
    return user_id, {"Authorization": f"Bearer {token}"}


def _insert_meeting(db, **overrides):
    doc = {
        "title": "모임",
        "description": "설명",
        "place": "기숙사",
        "scheduled_at": "2026-10-01T12:00:00+09:00",
        "deadline_at": "2026-10-01T11:00:00+09:00",
        "max_capacity": 5,
        "participants": [],
        "status": "open",
        "author_id": "author-default",
    }
    doc.update(overrides)
    result = db.meetings.insert_one(doc)
    return str(result.inserted_id)


@pytest.mark.integration
def test_profile_get_update_flow(client):
    _user_id, headers = _signup_and_login(client)

    get_res = client.get("/api/v1/profile/me", headers=headers)
    assert get_res.status_code == 200
    assert get_res.get_json()["success"] is True

    patch_res = client.patch(
        "/api/v1/profile/me",
        json={"nickname": "정글왕은열"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.get_json()["data"]["nickname"] == "정글왕은열"

    final_res = client.get("/api/v1/profile/me", headers=headers)
    assert final_res.status_code == 200
    assert final_res.get_json()["data"]["nickname"] == "정글왕은열"


@pytest.mark.integration
def test_profile_get_unauthorized(client):
    response = client.get("/api/v1/profile/me")
    assert response.status_code == 401


@pytest.mark.integration
def test_profile_patch_invalid_input(client):
    _user_id, headers = _signup_and_login(client)

    response = client.patch("/api/v1/profile/me", json={}, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_INPUT"


@pytest.mark.integration
def test_profile_meeting_tabs_split_by_schema(client, app):
    user_id, headers = _signup_and_login(client)

    with app.app_context():
        db = get_database(current_app)
        created_id = _insert_meeting(
            db,
            title="내가 만든 open",
            author_id=user_id,
            participants=[user_id],
            status="open",
        )
        _insert_meeting(
            db,
            title="내가 만든 closed",
            author_id=user_id,
            participants=[user_id],
            status="closed",
        )
        joined_open_id = _insert_meeting(
            db,
            title="참여중 모임",
            author_id="other-author",
            participants=[user_id, "another-user"],
            status="open",
        )
        joined_closed_id = _insert_meeting(
            db,
            title="참여했던 모임",
            author_id="other-author-2",
            participants=[user_id, "another-user"],
            status="closed",
        )
        _insert_meeting(
            db,
            title="상관없는 모임",
            author_id="someone-else",
            participants=["someone-else"],
            status="open",
        )

    res_created = client.get("/api/v1/profile/meetings/created", headers=headers)
    assert res_created.status_code == 200
    created = res_created.get_json()["data"]["meetings"]
    created_ids = {m["meeting_id"] for m in created}
    assert created_id in created_ids
    assert joined_open_id not in created_ids
    assert joined_closed_id not in created_ids

    res_joined_active = client.get("/api/v1/profile/meetings/joined/active", headers=headers)
    assert res_joined_active.status_code == 200
    joined_active = res_joined_active.get_json()["data"]["meetings"]
    joined_active_ids = {m["meeting_id"] for m in joined_active}
    assert joined_open_id in joined_active_ids
    assert created_id not in joined_active_ids
    assert all(m["status"] == "open" for m in joined_active)
    assert all(m["author_id"] != user_id for m in joined_active)

    res_joined_past = client.get("/api/v1/profile/meetings/joined/past", headers=headers)
    assert res_joined_past.status_code == 200
    joined_past = res_joined_past.get_json()["data"]["meetings"]
    joined_past_ids = {m["meeting_id"] for m in joined_past}
    assert joined_closed_id in joined_past_ids
    assert created_id not in joined_past_ids
    assert all(m["status"] == "closed" for m in joined_past)
    assert all(m["author_id"] != user_id for m in joined_past)


@pytest.mark.integration
def test_profile_meeting_endpoints_require_auth(client):
    assert client.get("/api/v1/profile/meetings/created").status_code == 401
    assert client.get("/api/v1/profile/meetings/joined/active").status_code == 401
    assert client.get("/api/v1/profile/meetings/joined/past").status_code == 401