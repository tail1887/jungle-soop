from flask import current_app

from app.db import get_database


class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        # TODO(feature/auth-signup, feature/auth-login-logout):
        # return get_database(current_app).users.find_one({"email": email})
        return None

    @staticmethod
    def create_user(user_doc: dict):
        # TODO(feature/auth-signup):
        # result = get_database(current_app).users.insert_one(user_doc)
        # return str(result.inserted_id)
        return None
