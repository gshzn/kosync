from collections.abc import Generator
import contextlib
import os
from pathlib import Path
from shutil import rmtree
from fastapi.testclient import TestClient
import pytest

from kosync_backend.main import app as kosync_backend_app


@contextlib.contextmanager
def updated_environment(environ: dict[str, str]) -> Generator[None]:
    """
    Temporarily updates the specified environment variables, and
    sets it back to the previous state afterwards.
    """
    old_env = os.environ.copy()

    os.environ.update({**old_env, **environ})

    yield

    for key in environ.keys():
        del os.environ[key]
    os.environ.update(old_env)


@pytest.fixture
def app_client() -> Generator[TestClient]:
    tmp_path = Path("/tmp/kosync/")
    sql_path = tmp_path / "kosync.db"
    uploads_path = tmp_path / "uploads"

    if tmp_path.exists():
        rmtree(tmp_path, ignore_errors=True)

    sql_path.parent.mkdir(parents=True, exist_ok=True)

    with updated_environment({"DATABASE_URL": f"sqlite:///{sql_path}", "UPLOAD_DIR": str(uploads_path)}):
        with TestClient(kosync_backend_app) as client:
            yield client


def test_create_account(app_client: TestClient) -> None:
    response = app_client.post(
        "/auth/register",
        json={
            "email": (username := "foo@bar.baz"),
            "password": (password := "foobarbaz"),
        },
    )

    assert response.is_success

    response = app_client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )

    assert response.is_success
    assert (access_token := response.json()["access_token"])

    response = app_client.get("/auth/me", headers={
        "Authorization": f"Bearer {access_token}"
    })

    assert response.is_success
    assert response.json()["email"] == username


@pytest.fixture
def authenticated_app_client(app_client: TestClient) -> None:
    response = app_client.post(
        "/auth/register",
        json={
            "email": (username := "foo@bar.baz"),
            "password": (password := "foobarbaz"),
        },
    )

    assert response.is_success

    response = app_client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )

    assert response.is_success
    app_client.headers.setdefault("Authorization", "Bearer " + response.json()["access_token"])

    return app_client
 

def test_upload_books(authenticated_app_client: TestClient) -> None:
    dummy_book = Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"

    response = authenticated_app_client.post(
        "/books",
        files={"file": ("book.epub", dummy_book.read_bytes())},
    )

    assert response.is_success

    response = authenticated_app_client.get("/books/")

    assert response.is_success
    assert len(response.json()) == 1
