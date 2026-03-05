from pathlib import Path
from urllib.parse import quote

from flask import Blueprint, current_app, jsonify, g, request
from app.middleware.auth_guard import login_required
from app.models.user_repository import UserRepository
from app.models.meeting_repository import MeetingRepository
from werkzeug.utils import secure_filename

# 프로필 관련 API 블루프린트
profile_bp = Blueprint("profile_api", __name__, url_prefix="/api/v1/profile")

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def _build_default_avatar_url(user_id: str, nickname: str | None) -> str:
    seed = quote(nickname or user_id or "jungle-soop")
    return f"https://api.dicebear.com/9.x/identicon/svg?seed={seed}"

@profile_bp.route("/me", methods=["GET"])
@login_required # 인증된 사용자만 접근 가능
def get_my_profile():
    user_id = g.user_id # auth_guard가 담아준 ID 사용
    user = UserRepository.find_by_id(user_id)
    
    if not user:
        return jsonify({
            "success": False, 
            "error": {"code": "USER_NOT_FOUND", "message": "사용자를 찾을 수 없습니다."}
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "nickname": user.get("nickname"),
            "profile_image_url": user.get("profile_image_url") or _build_default_avatar_url(
                str(user.get("_id", "")),
                user.get("nickname"),
            ),
        },
        "message": "내 정보 조회 성공"
    }), 200

@profile_bp.route("/me", methods=["PATCH"])
@login_required # 수정할 때도 당연히 로그인필요
def update_my_profile():
    # 1. 클라이언트가 보낸 JSON 데이터 가져오기
    payload = request.get_json(silent=True) or {}
    new_nickname = (payload.get("nickname") or "").strip()

    # 2. 필수 값 체크 (빈 닉네임은 허용하지 않음)
    if not new_nickname:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_INPUT", "message": "수정할 닉네임을 입력해주세요."}
        }), 400

    # 3. DB 업데이트 (g.user_id 사용)
    user_id = g.user_id
    updated = UserRepository.update_user(user_id, {"nickname": new_nickname})
    if not updated:
        return jsonify({
            "success": False,
            "error": {"code": "USER_NOT_FOUND", "message": "사용자를 찾을 수 없습니다."}
        }), 404

    return jsonify({
        "success": True,
        "data": {"nickname": new_nickname},
        "message": "프로필 수정 성공!"
    }), 200


@profile_bp.route("/me/avatar", methods=["POST"])
@login_required
def upload_my_avatar():
    user_id = g.user_id
    user = UserRepository.find_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": {"code": "USER_NOT_FOUND", "message": "사용자를 찾을 수 없습니다."}
        }), 404

    image_file = request.files.get("avatar")
    if image_file is None or not image_file.filename:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_INPUT", "message": "업로드할 이미지 파일이 필요합니다."}
        }), 400

    filename = secure_filename(image_file.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_INPUT", "message": "지원하지 않는 이미지 형식입니다."}
        }), 400

    upload_root = Path(current_app.static_folder) / "uploads" / "avatars"
    upload_root.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{user_id}.{extension}"
    save_path = upload_root / stored_filename
    image_file.save(save_path)

    profile_image_url = f"/static/uploads/avatars/{stored_filename}"
    updated = UserRepository.update_user(user_id, {"profile_image_url": profile_image_url})
    if not updated:
        return jsonify({
            "success": False,
            "error": {"code": "USER_NOT_FOUND", "message": "사용자를 찾을 수 없습니다."}
        }), 404

    return jsonify({
        "success": True,
        "data": {"profile_image_url": profile_image_url},
        "message": "프로필 이미지가 업데이트되었습니다."
    }), 200

@profile_bp.route("/meetings/created", methods=["GET"])  
@login_required  
def get_created_meetings():
    user_id = g.user_id
    meetings = MeetingRepository.find_created_meetings_by_user(user_id)

    def serialize_meeting(doc):
        participants = doc.get("participants", [])
        return {
            "meeting_id": str(doc["_id"]),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "author_id": doc.get("author_id"),
            "status": doc.get("status"),
            "max_capacity": doc.get("max_capacity"),
            "participants": participants,
            "participant_count": len(participants),
            "place": doc.get("place"),
            "scheduled_at": doc.get("scheduled_at"),
            "deadline_at": doc.get("deadline_at") or doc.get("scheduled_at"),
        }

    return jsonify({
        "success": True,
        "data": {
            "type": "created",
            "meetings": [serialize_meeting(m) for m in meetings],
        },
        "message": "내가 만든 모임 목록 조회 성공",
    }), 200


@profile_bp.route("/meetings/joined/active", methods=["GET"])
@login_required
def get_joined_active_meetings():
    """
    내가 현재 참여 중인(진행 중인) 모임 목록 조회 API
    GET /api/v1/profile/meetings/joined/active
    """
    user_id = g.user_id
    meetings = MeetingRepository.find_joined_active_meetings_by_user(user_id)

    def serialize_meeting(doc):
        participants = doc.get("participants", [])
        return {
            "meeting_id": str(doc["_id"]),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "author_id": doc.get("author_id"),
            "status": doc.get("status"),
            "max_capacity": doc.get("max_capacity"),
            "participants": participants,
            "participant_count": len(participants),
            "place": doc.get("place"),
            "scheduled_at": doc.get("scheduled_at"),
            "deadline_at": doc.get("deadline_at") or doc.get("scheduled_at"),
        }

    return jsonify({
        "success": True,
        "data": {
            "type": "joined_active",
            "meetings": [serialize_meeting(m) for m in meetings],
        },
        "message": "내가 참여 중인 모임 목록 조회 성공",
    }), 200

@profile_bp.route("/meetings/joined/past", methods=["GET"])
@login_required
def get_joined_past_meetings():
    """
    내가 참여했던(종료/지난) 모임 목록 조회 API
    GET /api/v1/profile/meetings/joined/past
    """
    user_id = g.user_id
    meetings = MeetingRepository.find_joined_past_meetings_by_user(user_id)

    def serialize_meeting(doc):
        participants = doc.get("participants", [])
        return {
            "meeting_id": str(doc["_id"]),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "author_id": doc.get("author_id"),
            "status": doc.get("status"),
            "max_capacity": doc.get("max_capacity"),
            "participants": participants,
            "participant_count": len(participants),
            "place": doc.get("place"),
            "scheduled_at": doc.get("scheduled_at"),
            "deadline_at": doc.get("deadline_at") or doc.get("scheduled_at"),
        }

    return jsonify({
        "success": True,
        "data": {
            "type": "joined_past",
            "meetings": [serialize_meeting(m) for m in meetings],
        },
        "message": "내가 참여했던 모임 목록 조회 성공",
    }), 200