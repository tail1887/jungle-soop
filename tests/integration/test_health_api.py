import pytest


@pytest.mark.integration
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@pytest.mark.integration
def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.integration
def test_index_redirects_to_meetings_when_access_token_exists(client):
    client.set_cookie("access_token", "dummy-token")
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/meetings")


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
    assert b'id="login-submit-button"' in response.data
    assert b"id=\"nav-logout-button\"" not in response.data
    assert b"/static/js/auth.js" in response.data


@pytest.mark.integration
def test_signup_page_has_auth_form_and_message(client):
    response = client.get("/signup")
    assert response.status_code == 200
    assert b'id="signup-form"' in response.data
    assert b'id="signup-message"' in response.data
    assert b'id="signup-password-confirm"' in response.data
    assert b'id="signup-submit-button"' in response.data
    assert b"id=\"nav-logout-button\"" not in response.data
    assert b"/static/js/auth.js" in response.data


@pytest.mark.integration
def test_default_pages_show_logout_button_in_nav(client):
    response = client.get("/meetings")
    assert response.status_code == 200
    assert b"id=\"nav-logout-button\"" in response.data
    assert b"/static/js/nav.js" in response.data


@pytest.mark.integration
def test_meeting_list_page_has_api_bound_components(client):
    response = client.get("/meetings")
    assert response.status_code == 200
    assert b'id="meetings-list"' in response.data
    assert b'id="meetings-refresh-button"' in response.data
    assert b'id="meetings-list-message"' in response.data
    assert b"/static/js/meetings.js" in response.data


@pytest.mark.integration
def test_meeting_create_page_has_form_components(client):
    response = client.get("/meetings/new")
    assert response.status_code == 200
    assert b'id="meeting-create-form"' in response.data
    assert b'id="meeting-create-message"' in response.data
    assert b'id="meeting-create-submit-button"' in response.data
    assert b"/static/js/meetings.js" in response.data


@pytest.mark.integration
def test_meeting_detail_page_has_detail_components(client):
    response = client.get("/meetings/sample-1")
    assert response.status_code == 200
    assert b'id="meeting-detail-root"' in response.data
    assert b'data-meeting-id="sample-1"' in response.data
    assert b'id="meeting-detail-refresh-button"' in response.data
    assert b"/static/js/meetings.js" in response.data
