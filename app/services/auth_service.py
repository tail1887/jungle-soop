from app.models.user_repository import UserRepository
from app.utils.security import hash_password


class AuthService:
    @staticmethod
    def signup(payload: dict) -> dict:
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""
        nickname = (payload.get("nickname") or "").strip()

        if not email or not password or not nickname:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "필수값이 누락되었습니다.",
                    },
                },
            }

        if "@" not in email:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "이메일 형식을 확인해주세요.",
                    },
                },
            }

        if UserRepository.find_by_email(email):
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "EMAIL_ALREADY_EXISTS",
                        "message": "이미 가입된 이메일입니다.",
                    },
                },
            }

        user_id = UserRepository.create_user(
            {
                "email": email,
                "password_hash": hash_password(password),
                "nickname": nickname,
            }
        )

        return {
            "status_code": 201,
            "body": {"success": True, "data": {"user_id": user_id}},
        }

    @staticmethod
    def login(payload: dict) -> dict:
        # TODO(feature/auth-login-logout):
        # 이메일/비밀번호 검증 후 JWT(access/refresh) 발급 구현
        return _not_implemented("AUTH_LOGIN_NOT_IMPLEMENTED")

    @staticmethod
    def logout() -> dict:
        # TODO(feature/auth-login-logout):
        # 토큰 폐기 전략(블랙리스트/리프레시 토큰 회수) 구현
        return _not_implemented("AUTH_LOGOUT_NOT_IMPLEMENTED")


def _not_implemented(code: str) -> dict:
    return {
        "status_code": 501,
        "body": {
            "success": False,
            "error": {
                "code": code,
                "message": "아직 구현되지 않은 기능입니다.",
            },
        },
    }
