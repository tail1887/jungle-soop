from flask import Flask

from app.api.auth_api import auth_bp
from app.api.meetings_api import meetings_bp
from app.api.profile_api import profile_bp

def register_api_routes(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(profile_bp)
