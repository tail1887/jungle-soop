import os
from flask import Flask
from app.api.auth_api import auth_bp
from app.db import init_mongo 

def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/jungle_soop")

    init_mongo(app)

    from app.routes import register_routes
    register_routes(app)
    app.register_blueprint(auth_bp)
    
    return app