from flask import Flask, jsonify


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "jungle-soop",
                "message": "Flask app is running.",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})
