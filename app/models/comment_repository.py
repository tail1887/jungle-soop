from flask import current_app

from app.db import get_database


class CommentRepository:
    @staticmethod
    def create(comment_doc: dict) -> str:
        db = get_database(current_app)
        result = db.comments.insert_one(comment_doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_meeting_id(meeting_id: str) -> list:
        db = get_database(current_app)
        cursor = db.comments.find({"meeting_id": meeting_id}).sort("created_at", 1)
        return list(cursor)

    @staticmethod
    def find_by_id(comment_id: str) -> dict | None:
        from bson import ObjectId

        db = get_database(current_app)
        try:
            oid = ObjectId(comment_id)
        except Exception:
            return None
        return db.comments.find_one({"_id": oid})

    @staticmethod
    def delete_by_id(comment_id: str) -> bool:
        from bson import ObjectId

        db = get_database(current_app)
        try:
            oid = ObjectId(comment_id)
        except Exception:
            return False
        result = db.comments.delete_one({"_id": oid})
        return result.deleted_count > 0
