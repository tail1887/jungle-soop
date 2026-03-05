from flask import current_app
from app.db import get_database


class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        return get_database(current_app).users.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id: str):
        from bson import ObjectId
        db = get_database(current_app)
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        return db.users.find_one({"_id": oid})

    @staticmethod
    def create_user(user_doc: dict):
        result = get_database(current_app).users.insert_one(user_doc)
        return str(result.inserted_id)
