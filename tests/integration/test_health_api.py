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
