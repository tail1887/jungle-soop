from flask import current_app
from app.models.user_repository import find_by_email, create_user
from app.utils.security import hash_password

def signup(db, payload):
    #이메일이나 패스워드가 채워지지 않은경우 false리턴
    if not payload.get('email') or not payload.get('password'):
        return False, {"code": "INVALID_INPUT", "message": "필수값이 누락되었습니다."}, 400
    #이메일이 이미 존재하는 경우 false리턴
    if find_by_email(db, payload['email']):
        return False, {"code": "EMAIL_ALREADY_EXISTS", "message": "이미 가입된 이메일입니다."}, 409

    user_data = {
        "email": payload['email'],
        "password": hash_password(payload['password']),
        "nickname": payload.get('nickname', '')
    }
    user_id = create_user(db, user_data)
    return True, {"user_id": user_id}, 201
