from app.models.user_repository import UserRepository


class AuthService:
    @staticmethod
    def signup(payload: dict) -> dict:
        # TODO(feature/auth-signup):
        # 1) 필수 입력(email/password/nickname) 검증
        # 2) 이메일 형식 검증
        # 3) UserRepository.find_by_email() 중복 체크
        # 4) 비밀번호 해시 후 UserRepository.create_user() 호출
        return _not_implemented("AUTH_SIGNUP_NOT_IMPLEMENTED")

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
