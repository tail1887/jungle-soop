from flask import current_app
from app.db import get_database


class MeetingRepository:
    @staticmethod
    def create(meeting_doc: dict):
        # TODO(feature/meetings-crud)
        db = get_database(current_app)
        result = db.meetings.insert_one(meeting_doc)
        # return the string form of the ObjectId so callers can serialize
        return str(result.inserted_id)

    @staticmethod
    def update_by_id(meeting_id: str, update_doc: dict):
        # TODO(feature/meetings-crud)
        from bson import ObjectId

        db = get_database(current_app)
        result = db.meetings.update_one(
            {"_id": ObjectId(meeting_id)},{"$set": update_doc}
        )
        # return True if a document was actually matched (exists)
        return result.matched_count > 0

    @staticmethod
    def delete_by_id(meeting_id: str):
        # TODO(feature/meetings-crud)
        from bson import ObjectId

        db = get_database(current_app)
        result = db.meetings.delete_one({"_id": ObjectId(meeting_id)})
        return result.deleted_count > 0

    @staticmethod
    def find_all(query: dict):
        # basic implementation: ignore filters for now, return all
        db = get_database(current_app)
        cursor = db.meetings.find(query or {})
        return list(cursor)

    @staticmethod
    def find_by_id(meeting_id: str):
        # simple lookup by _id, returning the document or None
        from bson import ObjectId

        db = get_database(current_app)
        try:
            oid = ObjectId(meeting_id)
        except Exception:
            return None
        return db.meetings.find_one({"_id": oid})

    @staticmethod
    def add_participant(meeting_id: str, user_id: str):
        # $addToSet 기반 참여 처리 (중복 방지)
        from bson import ObjectId

        db = get_database(current_app)
        result = db.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$addToSet": {"participants": user_id}},
        )
        # matched_count > 0: 모임 존재 여부, modified_count > 0: 실제로 추가됐는지 (중복 아님)
        return result.matched_count > 0, result.modified_count > 0

    @staticmethod
    def remove_participant(meeting_id: str, user_id: str):
        # $pull 기반 참여 취소 처리
        from bson import ObjectId

        db = get_database(current_app)
        result = db.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$pull": {"participants": user_id}},
        )
        # matched_count > 0: 모임 존재 여부, modified_count > 0: 실제로 제거됐는지
        return result.matched_count > 0, result.modified_count > 0

    @staticmethod
    def find_by_host_id(host_id: str):
        """host_id 가 주어진 사용자인 모임 목록 (방장 모임 목록)"""
        db = get_database(current_app)
        cursor = db.meetings.find({"host_id": host_id})
        return list(cursor)

    @staticmethod
    def find_created_meetings_by_user(user_id: str):
        """user_id 가 생성한 모임 목록 (host_id == user_id)"""
        # find_by_host_id 에 위임
        return MeetingRepository.find_by_host_id(user_id)

    @staticmethod
    def find_joined_active_meetings_by_user(user_id: str):
        db = get_database(current_app)
        cursor = db.meetings.find({
            "participants": user_id,
            "status": "active",
            "host_id": {"$ne": user_id},
        })
        return list(cursor)

    @staticmethod
    def find_joined_past_meetings_by_user(user_id: str):
        """
        사용자가 과거에 참여했던(종료된) 모임 목록 조회.
        - participants 배열에 user_id 가 포함
        - status 가 'closed' 또는 'finished' 등 'active' 가 아닌 값
        """
        db = get_database(current_app)
        cursor = db.meetings.find({
            "participants": user_id,
            "status": {"$ne": "active"},
            "host_id": {"$ne": user_id},
        })
        return list(cursor)