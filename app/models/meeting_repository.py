from flask import current_app

from app.db import get_database


class MeetingRepository:
    @staticmethod
    def create(meeting_doc: dict):
        # TODO(feature/meetings-crud)
        return None

    @staticmethod
    def update_by_id(meeting_id: str, update_doc: dict):
        # TODO(feature/meetings-crud)
        return None

    @staticmethod
    def delete_by_id(meeting_id: str):
        # TODO(feature/meetings-crud)
        return None

    @staticmethod
    def find_all(query: dict):
        # TODO(feature/meetings-query)
        return []

    @staticmethod
    def find_by_id(meeting_id: str):
        # TODO(feature/meetings-query)
        return None

    @staticmethod
    def add_participant(meeting_id: str, user_id: str):
        # TODO(feature/meetings-join): $addToSet 기반 참여 처리
        return None

    @staticmethod
    def remove_participant(meeting_id: str, user_id: str):
        # TODO(feature/meetings-join)
        return None
