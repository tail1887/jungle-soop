from flask import Blueprint, request, jsonify, current_app
from app.services import auth_service 
from app.db import get_database 
from app.middleware.auth_guard import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth') #blueprint: flask에서 기능별로 코드를 나눔

def format_response(is_success, result, status_code):
    if is_success:
        return jsonify({"success": True, "data": result}), status_code
    return jsonify({"success": False, "error": result}), status_code

@auth_bp.post('/signup')
def api_signup():
    db = get_database(current_app)
    return format_response(*auth_service.signup(db, request.get_json()))

@auth_bp.post('/login')
def api_login():
    db = get_database(current_app)
    return format_response(*auth_service.login(db, request.get_json()))

@auth_bp.post('/logout')
def api_logout():
    return format_response(*auth_service.logout())
