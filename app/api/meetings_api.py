from flask import Blueprint, jsonify, request

from app.services.meeting_service import MeetingService

meetings_bp = Blueprint("meetings_api", __name__, url_prefix="/api/v1/meetings")


@meetings_bp.post("")
def create_meeting():
    payload = request.get_json(silent=True) or {}
    result = MeetingService.create(payload)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.patch("/<meeting_id>")
def update_meeting(meeting_id: str):
    payload = request.get_json(silent=True) or {}
    result = MeetingService.update(meeting_id, payload)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.delete("/<meeting_id>")
def delete_meeting(meeting_id: str):
    result = MeetingService.delete(meeting_id)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.get("")
def list_meetings():
    query = request.args.to_dict()
    result = MeetingService.list(query)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.get("/<meeting_id>")
def get_meeting_detail(meeting_id: str):
    result = MeetingService.get_detail(meeting_id)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.post("/<meeting_id>/join")
def join_meeting(meeting_id: str):
    result = MeetingService.join(meeting_id)
    return jsonify(result["body"]), result["status_code"]


@meetings_bp.delete("/<meeting_id>/join")
def cancel_join_meeting(meeting_id: str):
    result = MeetingService.cancel_join(meeting_id)
    return jsonify(result["body"]), result["status_code"]
