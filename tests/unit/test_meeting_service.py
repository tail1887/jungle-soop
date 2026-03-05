
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
def test_list_meetings_success(monkeypatch):
    # MeetingRepository.find_all을 mock 처리
    from bson import ObjectId
    mock_meetings = [
        {"_id": ObjectId("507f1f77bcf86cd799439011"), "title": "모임1", "status": "open", "created_at": "2026-04-01"},
        {"_id": ObjectId("507f1f77bcf86cd799439012"), "title": "모임2", "status": "open", "created_at": "2026-04-02"},
    ]
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_all", lambda query: mock_meetings)
    
    result = MeetingService.list({"page": 1, "per_page": 10})
    assert result["status_code"] == 200
    assert result["body"]["success"] is True
    assert len(result["body"]["data"]["meetings"]) == 2
    assert result["body"]["data"]["pagination"]["total_count"] == 2

def test_get_meeting_detail_success(monkeypatch):
    # MeetingRepository.find_by_id를 mock 처리
    from bson import ObjectId
    mock_meeting = {"_id": ObjectId("507f1f77bcf86cd799439011"), "title": "테스트 모임", "place": "강릉"}
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: mock_meeting)
    
    result = MeetingService.get_detail("507f1f77bcf86cd799439011")
    assert result["status_code"] == 200
    assert result["body"]["success"] is True
    assert result["body"]["data"]["title"] == "테스트 모임"

def test_get_meeting_detail_not_found(monkeypatch):
    # 존재하지 않는 모임 조회
    monkeypatch.setattr("app.models.meeting_repository.MeetingRepository.find_by_id", lambda id: None)
    
    result = MeetingService.get_detail("invalidid")
    assert result["status_code"] == 404
    assert result["body"]["success"] is False
    assert result["body"]["error"]["code"] == "MEETING_NOT_FOUND"