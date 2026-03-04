import jwt
import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(hashed_password: str, password: str) -> bool:
    return check_password_hash(hashed_password, password)

def generate_token(user_id: str, expires_in_hours: int = 1) -> str:
    expire_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expires_in_hours)
    
    payload = {
        "user_id": str(user_id),  
        "exp": int(expire_time.timestamp())
    }
    
    return jwt.encode(payload, current_app.config.get('SECRET_KEY', 'default-secret-key'), algorithm='HS256')