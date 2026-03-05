
import pytest
from app.services.meeting_service import MeetingService

class DummySession(dict):
    def get(self, key, default=None):
        return super().get(key, default)

@pytest.fixture(autouse=True)
def patch_flask_session(monkeypatch):
    # flask.session을 더미로 대체
    monkeypatch.setattr("flask.session", DummySession({"user_id": "user1"}))

def test_create_meeting_success(monkeypatch):
    # MeetingRepository.create를 mock 처리
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.create", lambda doc: "dummyid")
    payload = {
        "title": "테스트",
        "place": "장소",
        "scheduled_at": "2026-04-01T12:00:00+09:00",
        "max_capacity": 5,
    }
    result = MeetingService.create(payload)
    assert result["status_code"] == 201
    assert result["body"]["data"]["meeting_id"] == "dummyid"

def test_update_meeting_success(monkeypatch):
    # MeetingRepository.find_by_id, update_by_id를 mock 처리
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: {"_id": id, "author_id": "user1"})
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.update_by_id", lambda id, doc: True)
    payload = {"title": "수정됨"}
    result = MeetingService.update("dummyid", payload)
    assert result["status_code"] == 200
    assert result["body"]["data"]["meeting_id"] == "dummyid"

def test_delete_meeting_success(monkeypatch):
    # MeetingRepository.find_by_id, delete_by_id를 mock 처리
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: {"_id": id, "author_id": "user1"})
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.delete_by_id", lambda id: True)
    result = MeetingService.delete("dummyid")
    assert result["status_code"] == 204
    assert result["body"] is None
def test_join_meeting_success(monkeypatch):
    # 성공적인 모임 참여
    meeting = {"_id": "id1", "max_capacity": 5, "participants": []}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: meeting)
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.add_participant", lambda id, uid: (True, True))
    
    result = MeetingService.join("id1")
    assert result["status_code"] == 201
    assert result["body"]["success"] is True
    assert result["body"]["data"]["meeting_id"] == "id1"

def test_join_meeting_duplicate(monkeypatch):
    # 중복 참여 시도 (409)
    meeting = {"_id": "id1", "max_capacity": 5, "participants": ["user1"]}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: meeting)
    
    result = MeetingService.join("id1")
    assert result["status_code"] == 409
    assert result["body"]["error"]["code"] == "ALREADY_JOINED"

def test_join_meeting_full(monkeypatch):
    # 정원 초과 (409)
    meeting = {"_id": "id1", "max_capacity": 2, "participants": ["user2", "user3"]}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: meeting)
    
    result = MeetingService.join("id1")
    assert result["status_code"] == 409
    assert result["body"]["error"]["code"] == "MEETING_FULL"

def test_join_meeting_not_found(monkeypatch):
    # 없는 모임 (404)
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: None)
    
    result = MeetingService.join("notfound")
    assert result["status_code"] == 404
    assert result["body"]["error"]["code"] == "MEETING_NOT_FOUND"

def test_cancel_join_success(monkeypatch):
    # 성공적인 참여 취소
    meeting = {"_id": "id1", "participants": ["user1"]}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: meeting)
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.remove_participant", lambda id, uid: (True, True))
    
    result = MeetingService.cancel_join("id1")
    assert result["status_code"] == 204
    assert result["body"] is None

def test_cancel_join_not_joined(monkeypatch):
    # 불참한 모임 취소 (409)
    meeting = {"_id": "id1", "participants": []}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: meeting)
    
    result = MeetingService.cancel_join("id1")
    assert result["status_code"] == 409
    assert result["body"]["error"]["code"] == "NOT_JOINED"

def test_cancel_join_not_found(monkeypatch):
    # 없는 모임 (404)
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: None)
    
    result = MeetingService.cancel_join("notfound")
    assert result["status_code"] == 404
    assert result["body"]["error"]["code"] == "MEETING_NOT_FOUND"