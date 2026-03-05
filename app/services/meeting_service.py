from app.models.meeting_repository import MeetingRepository


class MeetingService: # TODO(feature/meetings-crud): 서비스 레이어 구현, 비즈니스 로직과 Repository 호출 담당
    @staticmethod # TODO(feature/meetings-crud): create/update/delete 서비스 로직 구현
    def create(payload: dict) -> dict:
        # simple validation of required fields
        required = ["title", "place", "scheduled_at", "max_capacity"] # required fields per spec
        missing = [k for k in required if k not in payload] # check if any required field is missing
        if missing:# if there are missing fields, return 400 with error message
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_INVALID_PAYLOAD",
                        "message": f"필수 필드 누락: {', '.join(missing)}",
                    },
                },
            }

        # prepare document with defaults
        from datetime import datetime
        from flask import session # session에서 현재 로그인한 사용자 ID를 가져와 author_id로 설정, guard로 로그인 보장

        meeting_doc = payload.copy()
        meeting_doc.setdefault("description", "")
        # 현재 로그인한 사용자 ID를 author_id로 설정 (guard로 로그인 보장)
        meeting_doc["author_id"] = session.get("user_id")
        meeting_doc["participants"] = []
        meeting_doc["status"] = "open"
        now = datetime.utcnow()
        meeting_doc["created_at"] = now
        meeting_doc["updated_at"] = now

        meeting_id = MeetingRepository.create(meeting_doc)
        return {
            "status_code": 201,
            "body": {
                "success": True,
                "data": {"meeting_id": meeting_id},
                "message": "모임이 생성되었습니다.",
            },
        }

    @staticmethod
    def update(meeting_id: str, payload: dict) -> dict:
        # 작성자 권한 확인
        from flask import session

        meeting = MeetingRepository.find_by_id(meeting_id) # 존재 여부 확인 및 작성자 권한 검증

        if not meeting:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_NOT_FOUND",
                        "message": "해당 모임을 찾을 수 없습니다.",
                    },
                },
            }
        if str(meeting.get("author_id")) != session.get("user_id"): # 작성자만 수정 가능하도록 검증, session에서 현재 로그인한 사용자 ID와 비교
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "작성자만 수정할 수 있습니다.",
                    },
                },
            }

        # do not allow updating of participants/status/author_id
        # payload may be partial
        allowed = {"title", "description", "place", "scheduled_at", "max_capacity"}
        update_doc = {k: v for k, v in payload.items() if k in allowed}
        if not update_doc:
            # nothing to update
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_INVALID_PAYLOAD",
                        "message": "수정할 필드가 없습니다.",
                    },
                },
            }

        from datetime import datetime

        update_doc["updated_at"] = datetime.utcnow()

        updated = MeetingRepository.update_by_id(meeting_id, update_doc)
        if not updated:
            # 이 케이스는 사실상 위에서 걸렸으므로 도달하지 않음
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_NOT_FOUND",
                        "message": "해당 모임을 찾을 수 없습니다.",
                    },
                },
            }

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {"meeting_id": meeting_id},
                "message": "모임이 수정되었습니다.",
            },
        }

    @staticmethod
    def delete(meeting_id: str) -> dict:
        from flask import session

        meeting = MeetingRepository.find_by_id(meeting_id)
        if not meeting:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_NOT_FOUND",
                        "message": "해당 모임을 찾을 수 없습니다.",
                    },
                },
            }
        if str(meeting.get("author_id")) != session.get("user_id"):
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "작성자만 삭제할 수 있습니다.",
                    },
                },
            }

        deleted = MeetingRepository.delete_by_id(meeting_id)
        if not deleted:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_NOT_FOUND",
                        "message": "해당 모임을 찾을 수 없습니다.",
                    },
                },
            }
        # on success we follow spec: 204 no body
        return {"status_code": 204, "body": None}

    @staticmethod
    def list(query: dict) -> dict:
        # TODO(feature/meetings-query): 목록/필터/정렬/페이지네이션 구현
        return _not_implemented("MEETING_LIST_NOT_IMPLEMENTED")

    @staticmethod
    def get_detail(meeting_id: str) -> dict:
        # TODO(feature/meetings-query): 상세 조회 구현
        return _not_implemented("MEETING_DETAIL_NOT_IMPLEMENTED")

    @staticmethod
    def join(meeting_id: str) -> dict:
        # TODO(feature/meetings-join): 참여 처리/정원 검증 구현
        return _not_implemented("MEETING_JOIN_NOT_IMPLEMENTED")

    @staticmethod
    def cancel_join(meeting_id: str) -> dict:
        # TODO(feature/meetings-join): 참여 취소 처리 구현
        return _not_implemented("MEETING_CANCEL_JOIN_NOT_IMPLEMENTED")


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
