import pytest

from app import create_app
from app.db import _extract_db_name_from_uri, get_database


@pytest.mark.unit
def test_extract_db_name_from_uri():
    assert _extract_db_name_from_uri("mongodb://localhost:27017/jungle_soop") == "jungle_soop"
    assert _extract_db_name_from_uri("mongodb://localhost:27017") == "jungle_soop"


@pytest.mark.unit
def test_get_database_returns_configured_db():
    app = create_app()
    db = get_database(app)
    assert db.name == app.config["MONGO_DB_NAME"]
