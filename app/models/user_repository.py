from flask import current_app
from app.db import get_database

class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        # 주석을 풀고 실제 DB 조회가 작동하게 합니다.
        return get_database(current_app).users.find_one({"email": email})

    @staticmethod
    def create_user(user_doc: dict):
        # 회원가입 기능을 위해 이 부분도 미리 구현해둡니다.
        result = get_database(current_app).users.insert_one(user_doc)
        return str(result.inserted_id)