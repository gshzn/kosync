from collections.abc import Generator
import contextlib
import os
from pathlib import Path
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


@pytest.fixture(scope="session")
def app_client() -> Generator[TestClient]:
    sql_path = Path("/tmp/kosync.db")

    if sql_path.exists():
        sql_path.unlink()

    with updated_environment({"DATABASE_URL": f"sqlite:///{sql_path}"}):
        with TestClient(kosync_backend_app) as client:
            yield client

    sql_path.unlink()


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
