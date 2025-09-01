from collections.abc import Generator
import contextlib
import os
from pathlib import Path
from shutil import rmtree
from fastapi.testclient import TestClient
import pytest

from kosync_backend.main import get_app


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
        with TestClient(get_app(), raise_server_exceptions=True) as client:
            yield client


def test_upload_books(app_client: TestClient) -> None:
    dummy_book = Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"

    response = app_client.post(
        "/books",
        files={"file": ("book.epub", dummy_book.read_bytes())},
    )

    assert response.is_success
