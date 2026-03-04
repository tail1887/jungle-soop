import pytest

from app import create_app


@pytest.mark.unit
def test_create_app_returns_flask_instance():
    app = create_app()
    assert app.name == "app"


@pytest.mark.unit
def test_secret_key_has_default_value():
    app = create_app()
    assert app.config["SECRET_KEY"] is not None
