from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from kosync_backend.database import Synchronisation
from tests.conftest import upload_book


def test_synchronise_new_book(app_client: TestClient) -> None:
    upload_book(
        app_client,
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub",
    )

    response = app_client.post("/api/v1/sync", json=[])

    assert response.is_success

    new_book = response.json()[0]

    file_response = app_client.get(new_book["url"])
    assert file_response.is_success
    assert len(file_response.content) > 0

    response = app_client.post("/api/v1/sync", json=[new_book["id"]])

    assert response.is_success
    assert len(response.json()) == 0


def test_sync_records_returned_book_ids(
    app_client: TestClient, db_session: Session
) -> None:
    upload_book(
        app_client,
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub",
    )

    response = app_client.post("/api/v1/sync", json=[])
    assert response.is_success

    returned_ids = [book["id"] for book in response.json()]

    syncs = db_session.query(Synchronisation).all()
    assert len(syncs) == 1
    assert sorted(syncs[0].book_ids) == sorted(returned_ids)


def test_sync_records_empty_book_ids_when_up_to_date(
    app_client: TestClient, db_session: Session
) -> None:
    upload_book(
        app_client,
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub",
    )

    first_response = app_client.post("/api/v1/sync", json=[])
    book_id = first_response.json()[0]["id"]

    app_client.post("/api/v1/sync", json=[book_id])

    syncs = db_session.query(Synchronisation).order_by(Synchronisation.id).all()
    assert len(syncs) == 2
    assert syncs[1].book_ids == []


def test_each_sync_creates_a_separate_row(
    app_client: TestClient, db_session: Session
) -> None:
    upload_book(
        app_client,
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub",
    )

    app_client.post("/api/v1/sync", json=[])
    app_client.post("/api/v1/sync", json=[])

    syncs = db_session.query(Synchronisation).all()
    assert len(syncs) == 2


def test_sync_records_correct_user_id(
    app_client: TestClient, db_session: Session, dummy_user
) -> None:
    app_client.post("/api/v1/sync", json=[])

    syncs = db_session.query(Synchronisation).all()
    assert len(syncs) == 1
    assert syncs[0].user_id == UUID(dummy_user.id)
