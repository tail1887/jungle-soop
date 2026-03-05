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
        # 목록 조회: 필터/정렬/페이지네이션 구현
        from app.models.meeting_repository import MeetingRepository
        
        # 페이지네이션 기본값
        page = int(query.get('page', 1))
        per_page = int(query.get('per_page', 10))
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # 필터/정렬용 db 쿼리 구성
        filter_query = {}
        
        # 상태 필터 (예: status=open)
        if 'status' in query and query['status'] in ['open', 'closed']:
            filter_query['status'] = query['status']
        
        # 시간 범위 필터 (예: scheduled_at_gte)
        if 'scheduled_at_gte' in query:
            if 'scheduled_at' not in filter_query:
                filter_query['scheduled_at'] = {}
            filter_query['scheduled_at']['$gte'] = query['scheduled_at_gte']
        
        # 정렬 기본값: 최신순 (_id 역순)
        sort_field = '_id'
        sort_direction = -1  # 역순
        if 'sort' in query:
            sort_key = query['sort']
            if sort_key.startswith('-'):
                sort_field = sort_key[1:]
                sort_direction = -1
            else:
                sort_field = sort_key
                sort_direction = 1
        
        # 허용된 정렬 필드
        allowed_sort_fields = {'_id', 'created_at', 'updated_at', 'scheduled_at'}
        if sort_field not in allowed_sort_fields:
            sort_field = '_id'
            sort_direction = -1
        
        # DB에서 데이터 조회 (페이지네이션 포함)
        all_meetings = MeetingRepository.find_all(filter_query)
        
        # 정렬
        all_meetings = sorted(
            all_meetings,
            key=lambda x: x.get(sort_field, ''),
            reverse=(sort_direction == -1)
        )
        
        # 페이지네이션
        total_count = len(all_meetings)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_meetings = all_meetings[start_idx:end_idx]
        
        # ObjectId를 문자열로 변환
        for meeting in paginated_meetings:
            meeting['_id'] = str(meeting['_id'])
        
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {
                    "meetings": paginated_meetings,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_count": total_count,
                        "total_pages": (total_count + per_page - 1) // per_page,
                    },
                },
                "message": "모임 목록 조회 성공",
            },
        }

    @staticmethod
    def get_detail(meeting_id: str) -> dict:
        # 상세 조회: 모임 정보 반환
        from app.models.meeting_repository import MeetingRepository
        
        meeting = MeetingRepository.find_by_id(meeting_id) # 존재 여부 확인
        if not meeting: # 존재하지 않는 모임 조회 시 404 반환
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
        
        # ObjectId를 문자열로 변환
        meeting['_id'] = str(meeting['_id'])
        
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": meeting,
                "message": "모임 상세 조회 성공",
            },
        }

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
