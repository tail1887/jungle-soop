from app.models.meeting_repository import MeetingRepository


class MeetingService:
    @staticmethod
    def create(payload: dict) -> dict:
        # TODO(feature/meetings-crud): 모임 생성 로직 구현
        return _not_implemented("MEETING_CREATE_NOT_IMPLEMENTED")

    @staticmethod
    def update(meeting_id: str, payload: dict) -> dict:
        # TODO(feature/meetings-crud): 모임 수정 로직 구현
        return _not_implemented("MEETING_UPDATE_NOT_IMPLEMENTED")

    @staticmethod
    def delete(meeting_id: str) -> dict:
        # TODO(feature/meetings-crud): 모임 삭제 로직 구현
        return _not_implemented("MEETING_DELETE_NOT_IMPLEMENTED")

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
