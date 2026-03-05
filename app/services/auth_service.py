from app.models.user_repository import UserRepository
from app.utils.security import hash_password
from app.utils.security import check_password, generate_token


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
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""

        if not email or not password:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "이메일과 비밀번호를 입력해주세요.",
                    },
                },
            }

        user = UserRepository.find_by_email(email)

        if not user or not check_password(user["password_hash"], password):
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "이메일 또는 비밀번호가 일치하지 않습니다.",
                    },
                },
            }

        access_token = generate_token(str(user["_id"]))

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {
                    "user_id": str(user["_id"]),
                    "nickname": user.get("nickname", ""),
                    "access_token": access_token,
                },
                "message": "로그인 성공",
            },
        }

    @staticmethod
    def logout() -> dict:
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {},
                "message": "로그아웃 완료",
            },
        }

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