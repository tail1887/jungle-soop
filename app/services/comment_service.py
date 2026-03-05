from datetime import datetime, timezone

from app.models.comment_repository import CommentRepository
from app.models.meeting_repository import MeetingRepository


def _current_user_id() -> str | None:
    import flask

    if getattr(flask, "g", None):
        user_id = getattr(flask.g, "user_id", None)
        if user_id:
            return str(user_id)
    session_obj = getattr(flask, "session", None)
    if session_obj is not None:
        try:
            uid = session_obj.get("user_id")
            if uid:
                return str(uid)
        except RuntimeError:
            pass
    return None


def _serialize_comment(comment: dict) -> dict:
    from app.models.user_repository import UserRepository

    author_id = str(comment.get("author_id", ""))
    user = UserRepository.find_by_id(author_id)
    nickname = (user.get("nickname", author_id) if user else author_id) or author_id
    created_at = comment.get("created_at")
    if hasattr(created_at, "isoformat"):
        created_at = created_at.isoformat() + "Z"
    return {
        "comment_id": str(comment.get("_id", "")),
        "meeting_id": comment.get("meeting_id", ""),
        "author_id": author_id,
        "author_nickname": nickname,
        "body": comment.get("body", ""),
        "created_at": created_at or "",
    }


class CommentService:
    @staticmethod
    def create(meeting_id: str, payload: dict) -> dict:
        user_id = _current_user_id()
        if not user_id:
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {"code": "UNAUTHORIZED", "message": "로그인이 필요합니다."},
                },
            }

        meeting = MeetingRepository.find_by_id(meeting_id)
        if not meeting:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {"code": "MEETING_NOT_FOUND", "message": "해당 모임을 찾을 수 없습니다."},
                },
            }

        body = (payload.get("body") or "").strip()
        if not body:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {"code": "COMMENT_INVALID_PAYLOAD", "message": "댓글 내용을 입력해주세요."},
                },
            }

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        comment_doc = {
            "meeting_id": meeting_id,
            "author_id": user_id,
            "body": body,
            "created_at": now,
        }
        comment_id = CommentRepository.create(comment_doc)
        comment = CommentRepository.find_by_id(comment_id)
        return {
            "status_code": 201,
            "body": {
                "success": True,
                "data": _serialize_comment(comment),
                "message": "댓글이 등록되었습니다.",
            },
        }

    @staticmethod
    def list(meeting_id: str) -> dict:
        meeting = MeetingRepository.find_by_id(meeting_id)
        if not meeting:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {"code": "MEETING_NOT_FOUND", "message": "해당 모임을 찾을 수 없습니다."},
                },
            }

        comments = CommentRepository.find_by_meeting_id(meeting_id)
        items = [_serialize_comment(c) for c in comments]
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {"items": items},
                "message": "댓글 목록 조회 성공",
            },
        }

    @staticmethod
    def delete(meeting_id: str, comment_id: str) -> dict:
        user_id = _current_user_id()
        if not user_id:
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {"code": "UNAUTHORIZED", "message": "로그인이 필요합니다."},
                },
            }

        comment = CommentRepository.find_by_id(comment_id)
        if not comment:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {"code": "COMMENT_NOT_FOUND", "message": "해당 댓글을 찾을 수 없습니다."},
                },
            }
        if str(comment.get("meeting_id")) != meeting_id:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {"code": "COMMENT_NOT_FOUND", "message": "해당 댓글을 찾을 수 없습니다."},
                },
            }
        if str(comment.get("author_id")) != user_id:
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "error": {"code": "FORBIDDEN", "message": "작성자만 삭제할 수 있습니다."},
                },
            }

        CommentRepository.delete_by_id(comment_id)
        return {"status_code": 204, "body": None}
