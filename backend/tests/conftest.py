from collections.abc import Generator
import contextlib
from datetime import datetime
import os
from pathlib import Path
from shutil import rmtree

from fastapi.testclient import TestClient
import httpx
import pytest
from supabase_auth import User as SupabaseUser

from kosync_backend.main import get_app
from kosync_backend.user_middleware import (
    get_current_user_from_jwt,
    get_current_user_from_id,
)


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
def base_path() -> Generator[str]:
    tmp_path = Path("/tmp/kosync/")

    tmp_path.mkdir(exist_ok=True, parents=True)

    yield tmp_path

    if tmp_path.exists():
        rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def sql_path(base_path: Path) -> Generator[Path]:
    path = base_path / "kosync.db"

    yield path

    path.unlink()


@pytest.fixture
def uploads_path(base_path: Path) -> Generator[Path]:
    path = base_path / "uploads"

    path.mkdir(parents=True, exist_ok=True)

    yield path

    rmtree(path)


@pytest.fixture
def dummy_user() -> SupabaseUser:
    return SupabaseUser(
        id="6d50e42f-74c5-48f7-a42e-fe91e9ddcf69",
        email="test@example.com",
        aud="authenticated",
        created_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
        app_metadata={},
        user_metadata={},
    )


@pytest.fixture
def app_client(
    sql_path: Path, uploads_path: Path, dummy_user: SupabaseUser
) -> Generator[TestClient]:
    with updated_environment(
        {
            "DATABASE_URL": f"sqlite:///{sql_path}",
            "UPLOAD_DIR": str(uploads_path),
            "BASE_URL": "http://kosync.test/",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
        }
    ):
        app = get_app()

        # Mock auth dependencies
        app.dependency_overrides[get_current_user_from_jwt] = lambda: dummy_user
        app.dependency_overrides[get_current_user_from_id] = lambda: dummy_user

        with TestClient(app, raise_server_exceptions=True) as client:
            client.headers.update({"Authorization": "Bearer test-token"})
            yield client


def upload_book(app_client: TestClient, book: Path) -> httpx.Response:
    return app_client.post(
        "/api/v1/books",
        files={"file": ("book.epub", book.read_bytes())},
    )
