from flask import Blueprint, jsonify, g, request
from app.middleware.auth_guard import login_required
from app.models.user_repository import UserRepository

# 프로필 관련 API 블루프린트
profile_bp = Blueprint("profile_api", __name__, url_prefix="/api/v1/profile")

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
            "nickname": user.get("nickname")
        },
        "message": "내 정보 조회 성공"
    }), 200

@profile_bp.route("/me", methods=["PATCH"])
@login_required # 수정할 때도 당연히 로그인이 필요하겠죠?
def update_my_profile():
    # 1. 클라이언트가 보낸 JSON 데이터 가져오기
    payload = request.get_json()
    new_nickname = (payload.get("nickname") or "").strip()

    # 2. 필수 값 체크 (빈 닉네임은 허용하지 않음)
    if not new_nickname:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_INPUT", "message": "수정할 닉네임을 입력해주세요."}
        }), 400

    # 3. DB 업데이트 (g.user_id 사용)
    user_id = g.user_id
    UserRepository.update_user(user_id, {"nickname": new_nickname})

    return jsonify({
        "success": True,
        "data": {"nickname": new_nickname},
        "message": "프로필 수정 성공!"
    }), 200