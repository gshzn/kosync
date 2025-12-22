from pathlib import Path
from fastapi.testclient import TestClient

from tests.conftest import upload_book


def test_upload_books(app_client: TestClient, uploads_path: Path) -> None:
    dummy_book = (
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"
    )

    assert upload_book(app_client, dummy_book).is_success
    assert len(list(uploads_path.iterdir())) == 1

    assert len(app_client.get("/api/v1/books").json()) == 1


def test_update_book(app_client: TestClient) -> None:
    dummy_book = (
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"
    )

    response = upload_book(app_client, dummy_book)
    book_id = response.json()["id"]

    response = app_client.patch(
        url=f"/api/v1/books/{book_id}",
        json={"title": "Foo", "description": "Bar", "author": "Baz"},
    )

    assert response.is_success
    updated_book = app_client.get(f"/api/v1/books/{book_id}").json()

    assert updated_book["title"] == "Foo"
