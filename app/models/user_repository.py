from flask import current_app

from app.db import get_database


class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        return get_database(current_app).users.find_one({"email": email})

    @staticmethod
    def create_user(user_doc: dict):
        result = get_database(current_app).users.insert_one(user_doc)
        return str(result.inserted_id)
