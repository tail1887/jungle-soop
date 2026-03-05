from app.models.meeting_repository import MeetingRepository


class MeetingService:
    @staticmethod
    def create(payload: dict) -> dict:
        required = ["title", "place", "scheduled_at", "max_capacity"]
        missing = [k for k in required if k not in payload]
        if missing:
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

        author_id = _current_user_id()
        if not author_id:
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "로그인이 필요합니다.",
                    },
                },
            }

        from datetime import datetime
        meeting_doc = payload.copy()
        meeting_doc.setdefault("description", "")
        meeting_doc["author_id"] = author_id
        # The meeting author is considered an initial participant.
        meeting_doc["participants"] = [author_id]
        meeting_doc["deadline_at"] = meeting_doc.get("deadline_at") or meeting_doc["scheduled_at"]
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
        meeting = MeetingRepository.find_by_id(meeting_id)
        current_user_id = _current_user_id()

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
        if str(meeting.get("author_id")) != current_user_id:
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

        allowed = {
            "title",
            "description",
            "place",
            "scheduled_at",
            "deadline_at",
            "max_capacity",
            "status",
        }
        update_doc = {k: v for k, v in payload.items() if k in allowed}
        if not update_doc:
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

        status = update_doc.get("status")
        if status is not None and status not in {"open", "closed"}:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_INVALID_PAYLOAD",
                        "message": "status는 open 또는 closed만 허용됩니다.",
                    },
                },
            }

        from datetime import datetime

        update_doc["updated_at"] = datetime.utcnow()

        updated = MeetingRepository.update_by_id(meeting_id, update_doc)
        if not updated:
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
        meeting = MeetingRepository.find_by_id(meeting_id)
        current_user_id = _current_user_id()
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
        if str(meeting.get("author_id")) != current_user_id:
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
        return {"status_code": 204, "body": None}

    @staticmethod
    def list(query: dict) -> dict:
        page = _to_positive_int(query.get("page"), default=1)
        limit = _to_positive_int(query.get("limit"), default=10)

        if limit > 100:
            limit = 100

        filter_query = {}
        status = query.get("status")
        if status in {"open", "closed"}:
            filter_query["status"] = status

        all_meetings = MeetingRepository.find_all(filter_query)

        sort = query.get("sort", "latest")
        if sort == "deadline":
            sorted_meetings = sorted(
                all_meetings,
                key=lambda item: str(item.get("deadline_at") or item.get("scheduled_at", "")),
            )
        else:
            sorted_meetings = sorted(
                all_meetings,
                key=lambda item: str(item.get("_id", "")),
                reverse=True,
            )

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_meetings = sorted_meetings[start_idx:end_idx]

        total_count = len(all_meetings)
        items = [_serialize_meeting_summary(meeting) for meeting in paginated_meetings]

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "total_pages": (total_count + limit - 1) // limit,
                    },
                },
                "message": "모임 목록 조회 성공",
            },
        }

    @staticmethod
    def get_detail(meeting_id: str) -> dict:
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

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": _serialize_meeting_detail(meeting),
                "message": "모임 상세 조회 성공",
            },
        }

    @staticmethod
    def join(meeting_id: str) -> dict:
        user_id = _current_user_id()
        if not user_id:
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "로그인이 필요합니다.",
                    },
                },
            }

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

        participants = meeting.get("participants", [])
        if user_id in participants:
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "ALREADY_JOINED",
                        "message": "이미 참여한 모임입니다.",
                    },
                },
            }

        if meeting.get("status", "open") == "closed":
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_CLOSED",
                        "message": "이미 마감된 모임입니다.",
                    },
                },
            }

        max_capacity = meeting.get("max_capacity", 0)
        if len(participants) >= max_capacity:
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "MEETING_FULL",
                        "message": "모임 정원이 가득 찼습니다.",
                    },
                },
            }

        matched, modified = MeetingRepository.add_participant(meeting_id, user_id)
        if not matched:
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
        if not modified:
            refreshed = MeetingRepository.find_by_id(meeting_id) or meeting
            refreshed_participants = refreshed.get("participants", [])
            if user_id in refreshed_participants:
                return {
                    "status_code": 409,
                    "body": {
                        "success": False,
                        "error": {
                            "code": "ALREADY_JOINED",
                            "message": "이미 참여한 모임입니다.",
                        },
                    },
                }
            if len(refreshed_participants) >= refreshed.get("max_capacity", 0):
                return {
                    "status_code": 409,
                    "body": {
                        "success": False,
                        "error": {
                            "code": "MEETING_FULL",
                            "message": "모임 정원이 가득 찼습니다.",
                        },
                    },
                }

        refreshed = MeetingRepository.find_by_id(meeting_id) or meeting
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {
                    "meeting_id": meeting_id,
                    "participant_count": len(refreshed.get("participants", [])),
                    "status": refreshed.get("status", "open"),
                },
                "message": "모임 참여가 완료되었습니다.",
            },
        }

    @staticmethod
    def cancel_join(meeting_id: str) -> dict:
        user_id = _current_user_id()
        if not user_id:
            return {
                "status_code": 401,
                "body": {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "로그인이 필요합니다.",
                    },
                },
            }

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

        participants = meeting.get("participants", [])
        if user_id not in participants:
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "NOT_JOINED",
                        "message": "참여하지 않은 모임입니다.",
                    },
                },
            }

        matched, modified = MeetingRepository.remove_participant(meeting_id, user_id)
        if not matched:
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
        if not modified:
            return {
                "status_code": 409,
                "body": {
                    "success": False,
                    "error": {
                        "code": "NOT_JOINED",
                        "message": "참여하지 않은 모임입니다.",
                    },
                },
            }

        refreshed = MeetingRepository.find_by_id(meeting_id) or meeting
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "data": {
                    "meeting_id": meeting_id,
                    "participant_count": len(refreshed.get("participants", [])),
                    "status": refreshed.get("status", "open"),
                },
                "message": "모임 참여가 취소되었습니다.",
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


def _to_positive_int(value, default: int) -> int:
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return default
    return converted if converted > 0 else default


def _serialize_meeting_summary(meeting: dict) -> dict:
    participants = meeting.get("participants") or []
    return {
        "meeting_id": str(meeting.get("_id", "")),
        "title": meeting.get("title", ""),
        "place": meeting.get("place", ""),
        "scheduled_at": meeting.get("scheduled_at", ""),
        "deadline_at": meeting.get("deadline_at") or meeting.get("scheduled_at", ""),
        "participant_count": len(participants),
        "max_capacity": meeting.get("max_capacity"),
        "status": meeting.get("status", "open"),
    }


def _serialize_meeting_detail(meeting: dict) -> dict:
    participants = meeting.get("participants") or []
    return {
        "meeting_id": str(meeting.get("_id", "")),
        "title": meeting.get("title", ""),
        "description": meeting.get("description", ""),
        "place": meeting.get("place", ""),
        "scheduled_at": meeting.get("scheduled_at", ""),
        "deadline_at": meeting.get("deadline_at") or meeting.get("scheduled_at", ""),
        "participant_count": len(participants),
        "participants": [str(participant_id) for participant_id in participants],
        "max_capacity": meeting.get("max_capacity"),
        "status": meeting.get("status", "open"),
        "author_id": str(meeting.get("author_id", "")),
    }


def _current_user_id() -> str | None:
    import flask
    from flask import has_app_context, has_request_context

    if has_request_context() or has_app_context():
        try:
            user_id = getattr(flask.g, "user_id", None)
            if user_id:
                return str(user_id)
        except RuntimeError:
            pass

    session_obj = getattr(flask, "session", None)
    if session_obj is not None:
        try:
            session_user_id = session_obj.get("user_id")
            if session_user_id:
                return str(session_user_id)
        except RuntimeError:
            pass

    return None
