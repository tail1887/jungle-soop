from flask import Flask, jsonify, redirect, render_template, request, url_for
from app.middleware.auth_guard import login_required
from app.api.user_api import get_public_user_profile

def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        if request.cookies.get("access_token"):
            return redirect(url_for("meeting_list"))
        return redirect(url_for("login"))

    @app.get("/login")
    def login():
        return render_template("login.html", hide_nav=True)

    @app.get("/signup")
    def signup():
        return render_template("signup.html", hide_nav=True)

    @app.get("/meetings")
    def meeting_list():
        return render_template("meeting_list.html")

    @app.get("/meetings/new")
    def meeting_new():
        return render_template("meeting_form.html")

    @app.get("/meetings/<meeting_id>")
    def meeting_detail(meeting_id: str):
        return render_template("meeting_detail.html", meeting_id=meeting_id)

    @app.get("/meetings/<meeting_id>/edit")
    def meeting_edit(meeting_id: str):
        return render_template("meeting_edit.html", meeting_id=meeting_id)

    @app.get("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.get("/users/<user_id>")
    def user_profile_page(user_id: str):
        return render_template("user_profile.html", user_id=user_id)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/v1/users/<user_id>")
    @login_required
    def api_get_user_public_profile(user_id: str):
        user = get_public_user_profile(user_id)
        if user is None:
            return jsonify(
                {
                    "success": False,
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "사용자를 찾을 수 없습니다.",
                    },
                }
            ), 404

        return jsonify(
            {
                "success": True,
                "data": {
                    "user_id": user["id"],
                    "email": user["email"],
                    "nickname": user["nickname"],
                },
                "message": "사용자 프로필 조회 성공",
            }
        ), 200