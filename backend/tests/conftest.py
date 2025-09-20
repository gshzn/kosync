from collections.abc import Generator
import contextlib
import os
from pathlib import Path
from shutil import rmtree

from fastapi.testclient import TestClient
import httpx
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
def app_client(sql_path: Path, uploads_path: Path) -> Generator[TestClient]:
    with updated_environment(
        {
            "DATABASE_URL": f"sqlite:///{sql_path}",
            "UPLOAD_DIR": str(uploads_path),
            "BASE_URL": "http://kosync.test/"
        }
    ):
        with TestClient(get_app(), raise_server_exceptions=True) as client:
            yield client


def upload_book(app_client: TestClient, book: Path) -> httpx.Response:
    return app_client.post(
        "/books",
        files={"file": ("book.epub", book.read_bytes())},
    )
