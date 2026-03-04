from flask import Blueprint, jsonify, request, g
from app.middleware.auth_guard import login_required, check_ownership
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth_api", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/signup")
def signup():
    payload = request.get_json(silent=True) or {}
    result = AuthService.signup(payload)
    return jsonify(result["body"]), result["status_code"]


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    result = AuthService.login(payload)
    return jsonify(result["body"]), result["status_code"]


@auth_bp.post("/logout")
@login_required 
def logout():
    result = AuthService.logout()
    
    return jsonify(result["body"]), result["status_code"]

@auth_bp.delete("/test-permission/<owner_id>")
@login_required
def test_permission(owner_id):
    """권한 검증 로직을 테스트하기 위한 임시 API"""
    # check_ownership을 호출하여 권한이 없으면 바로 403 응답을 보냅니다.
    error_response = check_ownership(owner_id)
    if error_response:
        return error_response
        
    return jsonify({
        "success": True,
        "message": "권한 확인 완료"
    }), 200