
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
