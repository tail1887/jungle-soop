from functools import wraps

from flask import jsonify, request


def login_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        # TODO(feature/auth-guard): JWT 검증 로직 확정 후 guard 완성
        # 기대 포맷: Authorization: Bearer <access_token>
        auth_header = request.headers.get("Authorization", "")
        token = _extract_bearer_token(auth_header)
        if not token or not _is_valid_access_token(token):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "로그인이 필요합니다.",
                        },
                    }
                ),
                401,
            )
        return handler(*args, **kwargs)

    return wrapper


def _extract_bearer_token(auth_header: str) -> str:
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header.removeprefix("Bearer ").strip()


def _is_valid_access_token(token: str) -> bool:
    # TODO(feature/auth-guard): JWT 라이브러리(PyJWT 등)로 signature/exp/sub 검증 구현
    # 현재는 미구현 상태를 명시하기 위해 항상 False를 반환합니다.
    _ = token
    return False
