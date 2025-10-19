import os
from pathlib import Path

from kosync_backend.client_generator import ClientGenerator
from kosync_backend.config import Settings

def test_client_generation_fetches_all_resources() -> None:
    with ClientGenerator(Settings()) as client_generator:
        root_path = Path(str(client_generator.root_directory))

        assert set(os.listdir(root_path)) == {"usr",  "mnt"}

        nm_config = Path(client_generator.root_directory) / "mnt" / "onboard" / ".adds" / "nm" / "doc"

        assert "KoSync" in nm_config.read_text()
        assert (Path(client_generator.root_directory) / "mnt" / "onboard" / "kosync_client").exists()


def test_client_generation_generates_a_client_archive() -> None:
    with ClientGenerator(Settings()) as client_generator:
        archive_path = client_generator.generate("foo")

        assert archive_path.exists()