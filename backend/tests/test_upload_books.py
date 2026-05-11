from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from supabase_auth import User as SupabaseUser

from kosync_backend.database import UserUploadLimit
from tests.conftest import upload_book


DUMMY_BOOK = (
    Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"
)


def _insert_upload_limit(
    sql_path: Path, user_id: str, allowed_uploads: int | None
) -> None:
    engine = create_engine(f"sqlite:///{sql_path}")
    with Session(engine) as db:
        db.add(UserUploadLimit(user_id=UUID(user_id), allowed_uploads=allowed_uploads))
        db.commit()


def test_upload_books(app_client: TestClient, uploads_path: Path) -> None:
    assert upload_book(app_client, DUMMY_BOOK).is_success
    assert len(list(uploads_path.iterdir())) == 1

    assert len(app_client.get("/api/v1/books").json()) == 1


def test_update_book(app_client: TestClient) -> None:
    response = upload_book(app_client, DUMMY_BOOK)
    book_id = response.json()["id"]

    response = app_client.patch(
        url=f"/api/v1/books/{book_id}",
        json={"title": "Foo", "description": "Bar", "author": "Baz"},
    )

    assert response.is_success
    updated_book = app_client.get(f"/api/v1/books/{book_id}").json()

    assert updated_book["title"] == "Foo"


def test_default_limit_enforced_without_record(app_client: TestClient) -> None:
    """Default 5-book limit applies when no UserUploadLimit record exists."""
    for _ in range(5):
        assert upload_book(app_client, DUMMY_BOOK).is_success

    response = upload_book(app_client, DUMMY_BOOK)
    assert response.status_code == 400
    assert "Maximum number of books (5) reached" in response.json()["detail"]


def test_custom_limit_allows_more_uploads(
    app_client: TestClient, sql_path: Path, dummy_user: SupabaseUser
) -> None:
    """A UserUploadLimit record with allowed_uploads=8 overrides the default limit."""
    _insert_upload_limit(sql_path, dummy_user.id, allowed_uploads=8)

    # All 8 uploads should succeed (beyond the default of 5)
    for i in range(8):
        resp = upload_book(app_client, DUMMY_BOOK)
        assert resp.is_success, f"Upload {i + 1} failed unexpectedly: {resp.json()}"

    # The 9th upload should be rejected with the custom limit message
    response = upload_book(app_client, DUMMY_BOOK)
    assert response.status_code == 400
    assert "Maximum number of books (8) reached" in response.json()["detail"]


def test_null_allowed_uploads_falls_back_to_default(
    app_client: TestClient, sql_path: Path, dummy_user: SupabaseUser
) -> None:
    """A UserUploadLimit record with allowed_uploads=None falls back to the default."""
    _insert_upload_limit(sql_path, dummy_user.id, allowed_uploads=None)

    for _ in range(5):
        assert upload_book(app_client, DUMMY_BOOK).is_success

    response = upload_book(app_client, DUMMY_BOOK)
    assert response.status_code == 400
    assert "Maximum number of books (5) reached" in response.json()["detail"]
