from pathlib import Path
from fastapi.testclient import TestClient



def test_upload_books(app_client: TestClient, uploads_path: Path) -> None:
    dummy_book = Path(__file__).parent / "resources" / "Around the World in 28 Languages.epub"

    response = app_client.post(
        "/books",
        files={"file": ("book.epub", dummy_book.read_bytes())},
    )

    assert response.is_success
    assert len(list(uploads_path.iterdir()) ) == 1


