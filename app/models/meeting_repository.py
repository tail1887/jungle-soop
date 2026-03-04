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
            {"_id": ObjectId(meeting_id)}, {"$set": update_doc}
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
        # TODO(feature/meetings-join): $addToSet 기반 참여 처리
        return None

    @staticmethod
    def remove_participant(meeting_id: str, user_id: str):
        # TODO(feature/meetings-join)
        return None
