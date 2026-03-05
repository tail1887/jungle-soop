import pytest
from flask import current_app

from app.db import get_database
from app.models.meeting_repository import MeetingRepository


def get_auth_headers(client):
    """테스트용 계정으로 로그인하여 토큰 헤더를 생성하는 함수"""
    # 1. 테스트용 계정 생성 (이미 있으면 에러나겠지만 무시)
    client.post("/api/v1/auth/signup", json={
        "email": "test_user@example.com",
        "password": "password123",
        "nickname": "초기닉네임"
    })
    
    # 2. 로그인하여 토큰 받기
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test_user@example.com",
        "password": "password123"
    })
    token = login_res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_profile_api_flow(client):
    """[통합 테스트] 조회 -> 수정 -> 재조회 흐름 확인"""
    # 0. 로그인 헤더 준비
    headers = get_auth_headers(client)
    
    # 1. 초기 조회 (GET)
    get_res = client.get("/api/v1/profile/me", headers=headers)
    assert get_res.status_code == 200
    
    # 2. 닉네임 수정 (PATCH)
    new_name = "정글왕은열"
    patch_res = client.patch(
        "/api/v1/profile/me",
        json={"nickname": new_name},
        headers=headers
    )
    assert patch_res.status_code == 200
    assert patch_res.get_json()["data"]["nickname"] == new_name
    
    # 3. 수정 후 재조회 일관성 확인 (GET)
    final_res = client.get("/api/v1/profile/me", headers=headers)
    assert final_res.get_json()["data"]["nickname"] == new_name
    assert final_res.get_json()["success"] is True


@pytest.mark.integration
def test_get_profile_unauthorized(client):
    """[예외] 토큰 없이 접근 시 401 확인"""
    response = client.get("/api/v1/profile/me")
    assert response.status_code == 401


# ===== [추가 테스트] 프로필 기반 모임 목록 조회 API들 =====

@pytest.mark.integration
def test_get_joined_active_meetings_returns_only_active_joined(client, app):
    """
    /api/v1/profile/meetings/joined/active 는
    - participants 에 내가 포함되어 있고
    - status == 'active' 인 모임만 반환해야 한다.
    """
    headers = get_auth_headers(client)

    with app.app_context():
        db = get_database(current_app)
        db.meetings.delete_many({})
        user = db.users.find_one({"email": "test_user@example.com"})
        user_id = str(user["_id"])

@pytest.mark.integration
def test_meeting_type_queries_created_joined_active_joined_past(client, app):
    """
    [통합 테스트] 모임 유형별 조회(created / joined_active / joined_past) 검증

    시나리오:
    - 내가 만든(created) 모임 1개
    - 내가 참여 중인 active 모임 1개
    - 내가 과거에 참여했던 closed 모임 1개
    - 내가 상관없는 모임 몇 개 (필터링에서 제외)
    각 엔드포인트가 자기 타입에 맞는 것만 반환해야 한다.
    """
    headers = get_auth_headers(client)

    with app.app_context():
        db = get_database(current_app)
        db.meetings.delete_many({})

        # 로그인한 유저 조회
        user = db.users.find_one({"email": "test_user@example.com"})
        user_id = str(user["_id"])

        # 1) 내가 만든(created) 모임 1개
        created_id = MeetingRepository.create({
            "title": "내가 만든 모임",
            "description": "created",
            "host_id": user_id,
            "status": "active",
            "max_participants": 10,
            "participants": [user_id],
        })

        # 2) 내가 참여 중인 active 모임 1개 (host는 다른 사람)
        joined_active_id = MeetingRepository.create({
            "title": "참여 중 모임",
            "description": "joined_active",
            "host_id": "other_host",
            "status": "active",
            "max_participants": 10,
            "participants": [user_id],
        })

        # 3) 내가 과거에 참여했던 closed 모임 1개
        joined_past_id = MeetingRepository.create({
            "title": "지난 모임",
            "description": "joined_past",
            "host_id": "other_host2",
            "status": "closed",
            "max_participants": 5,
            "participants": [user_id],
        })

        # 4) 내가 상관없는 모임들 (필터에서 모두 제외되어야 함)
        MeetingRepository.create({
            "title": "남의 active 모임",
            "description": "other_active",
            "host_id": "someone_else",
            "status": "active",
            "max_participants": 3,
            "participants": ["someone_else"],
        })
        MeetingRepository.create({
            "title": "남의 지난 모임",
            "description": "other_past",
            "host_id": "someone_else",
            "status": "closed",
            "max_participants": 3,
            "participants": ["someone_else"],
        })

    # --- 1) 내가 만든(created) 모임 목록 조회 ---
    res_created = client.get("/api/v1/profile/meetings/created", headers=headers)
    assert res_created.status_code == 200
    body_created = res_created.get_json()
    assert body_created["success"] is True
    assert body_created["data"]["type"] == "created"

    created_ids = {m["id"] for m in body_created["data"]["meetings"]}
    assert created_id in created_ids
    # created 는 host_id == user_id 기준이므로 joined_active / joined_past 는 나오지 않아야 함
    assert joined_active_id not in created_ids
    assert joined_past_id not in created_ids

    # --- 2) 내가 참여 중인(active) 모임 목록 조회 ---
    res_joined_active = client.get(
        "/api/v1/profile/meetings/joined/active",
        headers=headers,
    )
    assert res_joined_active.status_code == 200
    body_joined_active = res_joined_active.get_json()
    assert body_joined_active["success"] is True
    assert body_joined_active["data"]["type"] == "joined_active"

    joined_active_ids = {m["id"] for m in body_joined_active["data"]["meetings"]}
    assert joined_active_id in joined_active_ids
    # created / joined_past 모임은 여기 포함되면 안 됨
    assert created_id not in joined_active_ids
    assert joined_past_id not in joined_active_ids
    assert all(m["status"] == "active" for m in body_joined_active["data"]["meetings"])

    # --- 3) 내가 참여했던(past) 모임 목록 조회 ---
    res_joined_past = client.get(
        "/api/v1/profile/meetings/joined/past",
        headers=headers,
    )
    assert res_joined_past.status_code == 200
    body_joined_past = res_joined_past.get_json()
    assert body_joined_past["success"] is True
    assert body_joined_past["data"]["type"] == "joined_past"

    joined_past_ids = {m["id"] for m in body_joined_past["data"]["meetings"]}
    assert joined_past_id in joined_past_ids
    # created / joined_active 모임은 여기 포함되면 안 됨
    assert created_id not in joined_past_ids
    assert joined_active_id not in joined_past_ids
    assert all(m["status"] != "active" for m in body_joined_past["data"]["meetings"])

    
@pytest.mark.integration
def test_meeting_tabs_data_and_authz_cases(client, app):
    """
    [통합 테스트] 모임 탭(created / joined_active / joined_past) 데이터 분류 및 권한 케이스 검증

    검증 내용:
    - 로그인하지 않으면 세 엔드포인트 모두 401
    - 로그인 후:
      - created: host_id == user_id 인 모임만
      - joined_active: participants 에 user_id 포함, status == active, host_id != user_id
      - joined_past: participants 에 user_id 포함, status != active, host_id != user_id
    """
    # 1) 권한: 비로그인 상태에서는 모두 401
    res_created_unauth = client.get("/api/v1/profile/meetings/created")
    res_joined_active_unauth = client.get("/api/v1/profile/meetings/joined/active")
    res_joined_past_unauth = client.get("/api/v1/profile/meetings/joined/past")

    assert res_created_unauth.status_code == 401
    assert res_joined_active_unauth.status_code == 401
    assert res_joined_past_unauth.status_code == 401

    # 2) 로그인 후, 더미 데이터 세팅
    headers = get_auth_headers(client)

    with app.app_context():
        db = get_database(current_app)
        db.meetings.delete_many({})

        user = db.users.find_one({"email": "test_user@example.com"})
        user_id = str(user["_id"])

        # created: 내가 만든(active) 모임
        created_id = MeetingRepository.create({
            "title": "내가 만든 active 모임",
            "description": "created_tab",
            "host_id": user_id,
            "status": "active",
            "max_participants": 10,
            "participants": [user_id],
        })

        # created: 내가 만든 past 모임 (status != active) -> created 탭에는 나오지만 joined_* 에는 안 나와야 함
        created_past_id = MeetingRepository.create({
            "title": "내가 만든 지난 모임",
            "description": "created_past",
            "host_id": user_id,
            "status": "closed",
            "max_participants": 5,
            "participants": [user_id],
        })

        # joined_active: 내가 참여 중인 active 모임 (host는 다른 사람)
        joined_active_id = MeetingRepository.create({
            "title": "참여 중 active 모임",
            "description": "joined_active_tab",
            "host_id": "other_host",
            "status": "active",
            "max_participants": 8,
            "participants": [user_id],
        })

        # joined_past: 내가 과거에 참여했던 모임 (status != active, host는 다른 사람)
        joined_past_id = MeetingRepository.create({
            "title": "참여했던 지난 모임",
            "description": "joined_past_tab",
            "host_id": "other_host2",
            "status": "closed",
            "max_participants": 6,
            "participants": [user_id],
        })

        # 완전히 상관없는 모임들 (어느 탭에도 나타나면 안 됨)
        MeetingRepository.create({
            "title": "남의 active 모임",
            "description": "other_active",
            "host_id": "someone_else",
            "status": "active",
            "max_participants": 3,
            "participants": ["someone_else"],
        })
        MeetingRepository.create({
            "title": "남의 지난 모임",
            "description": "other_past",
            "host_id": "someone_else",
            "status": "closed",
            "max_participants": 3,
            "participants": ["someone_else"],
        })

    # --- created 탭 ---
    res_created = client.get("/api/v1/profile/meetings/created", headers=headers)
    assert res_created.status_code == 200
    body_created = res_created.get_json()
    assert body_created["success"] is True
    assert body_created["data"]["type"] == "created"

    created_ids = {m["id"] for m in body_created["data"]["meetings"]}
    # 내가 만든 두 모임은 모두 포함
    assert created_id in created_ids
    assert created_past_id in created_ids
    # joined_* 용 모임은 created 탭에는 없어야 함
    assert joined_active_id not in created_ids
    assert joined_past_id not in created_ids

    # --- joined_active 탭 ---
    res_joined_active = client.get("/api/v1/profile/meetings/joined/active", headers=headers)
    assert res_joined_active.status_code == 200
    body_joined_active = res_joined_active.get_json()
    assert body_joined_active["success"] is True
    assert body_joined_active["data"]["type"] == "joined_active"

    joined_active_ids = {m["id"] for m in body_joined_active["data"]["meetings"]}
    # 참여 중 active 모임만 포함
    assert joined_active_id in joined_active_ids
    # 내가 만든 모임들은 포함되면 안 됨
    assert created_id not in joined_active_ids
    assert created_past_id not in joined_active_ids
    # past joined 모임도 여기에 나오면 안 됨
    assert joined_past_id not in joined_active_ids
    # 조건(status == active, host_id != user_id) 확인
    assert all(m["status"] == "active" for m in body_joined_active["data"]["meetings"])
    assert all(m["host_id"] != user_id for m in body_joined_active["data"]["meetings"])
    assert all(user_id in m["participants"] for m in body_joined_active["data"]["meetings"])

    # --- joined_past 탭 ---
    res_joined_past = client.get("/api/v1/profile/meetings/joined/past", headers=headers)
    assert res_joined_past.status_code == 200
    body_joined_past = res_joined_past.get_json()
    assert body_joined_past["success"] is True
    assert body_joined_past["data"]["type"] == "joined_past"

    joined_past_ids = {m["id"] for m in body_joined_past["data"]["meetings"]}
    # 참여했던 past 모임만 포함
    assert joined_past_id in joined_past_ids
    # 내가 만든 모임들은 포함되면 안 됨
    assert created_id not in joined_past_ids
    assert created_past_id not in joined_past_ids
    # active joined 모임도 여기에 나오면 안 됨
    assert joined_active_id not in joined_past_ids
    # 조건(status != active, host_id != user_id) 확인
    assert all(m["status"] != "active" for m in body_joined_past["data"]["meetings"])
    assert all(m["host_id"] != user_id for m in body_joined_past["data"]["meetings"])
    assert all(user_id in m["participants"] for m in body_joined_past["data"]["meetings"])