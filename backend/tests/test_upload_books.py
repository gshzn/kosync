from pathlib import Path
from fastapi.testclient import TestClient

from tests.conftest import upload_book


def test_upload_books(app_client: TestClient, uploads_path: Path) -> None:
    dummy_book = (
        Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"
    )

    assert upload_book(app_client, dummy_book).is_success
    assert len(list(uploads_path.iterdir())) == 1
