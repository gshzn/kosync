from pathlib import Path

from fastapi.testclient import TestClient

from tests.conftest import upload_book


def test_synchronise_new_book(app_client: TestClient) -> None:
    upload_book(
        app_client,
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub",
    )

    response = app_client.post("/api/v1/sync", json=[])

    assert response.is_success
    assert len(response.json()) == 1

    new_book = response.json()[0]

    response = app_client.post("/api/v1/sync", json=[new_book["id"]])

    assert response.is_success
    assert len(response.json()) == 0
