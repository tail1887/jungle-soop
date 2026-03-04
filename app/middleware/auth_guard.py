from functools import wraps

from flask import jsonify, session


def login_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        # TODO(feature/auth-guard): 세션 키/인증 정책 확정 후 guard 완성
        if not session.get("user_id"):
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
