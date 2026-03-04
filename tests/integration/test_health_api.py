import pytest


@pytest.mark.integration
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@pytest.mark.integration
def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Jungle Soop" in response.data


@pytest.mark.integration
@pytest.mark.parametrize(
    "path",
    ["/login", "/signup", "/meetings", "/meetings/new", "/meetings/sample-1"],
)
def test_frontend_scaffold_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.integration
def test_login_page_has_auth_form_and_message(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'id="login-form"' in response.data
    assert b'id="login-message"' in response.data
    assert b"/static/js/auth.js" in response.data


@pytest.mark.integration
def test_signup_page_has_auth_form_and_message(client):
    response = client.get("/signup")
    assert response.status_code == 200
    assert b'id="signup-form"' in response.data
    assert b'id="signup-message"' in response.data
    assert b"/static/js/auth.js" in response.data
