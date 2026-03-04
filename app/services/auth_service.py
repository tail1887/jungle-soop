from app.models.user_repository import UserRepository
from app.utils.security import check_password, generate_token # 추가 임포트

class AuthService:
    @staticmethod
    def signup(payload: dict) -> dict:
        return _not_implemented("AUTH_SIGNUP_NOT_IMPLEMENTED")

    @staticmethod
    def login(payload: dict) -> dict:
        email = payload.get("email")
        password = payload.get("password")
        
        user = UserRepository.find_by_email(email)
        if not user or not check_password(user["password_hash"], password):
            return {
                "status_code": 401,
                "body": {"success": False, "error": {"code": "INVALID_INPUT", "message": "로그인 정보 불일치"}}
            }
        
        token = generate_token(str(user["_id"]))
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {"access_token": token}
            }
        }

    @staticmethod
    def logout() -> dict:
        return {
            "status_code": 200,
            "body": {"success": True, "data": {}, "message": "로그아웃 완료"}
        }

def _not_implemented(code: str) -> dict:
    return {
        "status_code": 501,
        "body": {
            "success": False,
            "error": {"code": code, "message": "아직 구현되지 않은 기능입니다."},
        },
    }