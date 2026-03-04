from app import create_app


def test_create_app_boots():
    app = create_app()
    assert app is not None


def test_index_route_returns_ok():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_health_route_returns_ok():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
