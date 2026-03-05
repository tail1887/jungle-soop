from flask import Flask, jsonify, redirect, render_template, request, url_for


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

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})
