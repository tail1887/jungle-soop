from functools import wraps
from flask import request, jsonify, current_app

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "success": False, 
                "error": {"code": "UNAUTHORIZED", "message": "토큰이 없습니다."}
            }), 401
        
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = payload['user_id'] 
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": {"code": "TOKEN_EXPIRED", "message": "만료된 토큰입니다."}}), 401
        except Exception:
            return jsonify({"success": False, "error": {"code": "INVALID_TOKEN", "message": "유효하지 않은 토큰입니다."}}), 401
            
        return f(*args, **kwargs)
    return decorated