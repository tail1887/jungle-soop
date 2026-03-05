from bson import ObjectId
from flask import current_app
from app.db import get_database

class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        return get_database(current_app).users.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id: str):
        return get_database(current_app).users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def create_user(user_doc: dict):
        result = get_database(current_app).users.insert_one(user_doc)
        return str(result.inserted_id)

    @staticmethod
    def update_user(user_id: str, update_data: dict):
    # $set을 사용하면 전달된 필드만 딱 골라서 수정합니다.
        return get_database(current_app).users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
