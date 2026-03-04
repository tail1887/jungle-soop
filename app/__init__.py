import os

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    # NOTE: keep a deterministic fallback for local boot.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/jungle_soop")
    app.config["MONGO_DB_NAME"] = os.getenv("MONGO_DB_NAME", "jungle_soop")

    from app.db import init_mongo

    init_mongo(app)

    from app.api import register_api_routes
    from app.routes import register_routes

    register_routes(app)
    register_api_routes(app)
    return app
