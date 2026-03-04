import pytest

from app import create_app


def pytest_collection_modifyitems(config, items):
    for item in items:
        path_parts = str(item.fspath).replace("\\", "/").split("/")
        if "tests" in path_parts and "integration" in path_parts:
            if "integration" not in item.keywords:
                item.add_marker(pytest.mark.integration)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()
