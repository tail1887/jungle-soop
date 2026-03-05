from functools import wraps
from flask import g, jsonify, request

from app.utils.security import decode_token


def login_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = _extract_bearer_token(auth_header)

        if not token:
            return _unauthorized_response()

        payload = decode_token(token)
        if not payload:
            return _unauthorized_response()

        user_id = payload.get("user_id")
        if not user_id:
            return _unauthorized_response()

        g.user_id = str(user_id)
        return handler(*args, **kwargs)

    return wrapper


def check_ownership(resource_owner_id: str):
    """현재 로그인한 유저가 해당 리소스의 주인인지 확인"""
    if str(g.user_id) != str(resource_owner_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "해당 권한이 없습니다.",
                    },
                }
            ),
            403,
        )
    return None


def _extract_bearer_token(auth_header: str) -> str:
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header.removeprefix("Bearer ").strip()


def _unauthorized_response():
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