from flask import Blueprint, jsonify, request
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
def logout():
    result = AuthService.logout()
    return jsonify(result["body"]), result["status_code"]