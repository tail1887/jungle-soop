from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    # NOTE: keep a deterministic fallback for local boot.
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or "dev-secret-key"

    from app.routes import register_routes

    register_routes(app)
    return app
