import json
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Self
from urllib.request import urlretrieve
from pathlib import Path

from fastapi import Request

from kosync_backend.config import Settings


class ClientGenerator:
    root_directory: Path
    _settings: Settings

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def __enter__(self) -> Self:
        self.root_directory = self._prepare_nickeldbus()
        self._prepare_client()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        shutil.rmtree(self.root_directory)

    def _download_latest_nickelmenu_version(self) -> Path:
        path, _ = urlretrieve(
            "https://github.com/pgaskin/NickelMenu/releases/download/v0.5.4/KoboRoot.tgz"
        )

        return Path(path)

    def _prepare_nickeldbus(self) -> Path:
        tmp_dir = TemporaryDirectory(delete=False)

        tar = tarfile.open(self._download_latest_nickelmenu_version(), "r:gz")
        tar.extractall(path=tmp_dir.name, filter="tar")
        tar.close()

        return Path(tmp_dir.name)

    def _nickelmenu_config(self) -> str:
        return (
            "experimental:menu_main_15505_label:KoSync\n"
            "menu_item :main    :Synchronise        :cmd_spawn          :quiet:/mnt/onboard/kosync_client"
        )

    def _prepare_client(self) -> None:
        client_path = Path(self._settings.client_path)

        if not client_path.exists():
            raise ValueError(
                f"No client executable found at the set path: {client_path.name}"
            )

        shutil.copyfile(
            client_path, Path(self.root_directory) / "mnt" / "onboard" / "kosync_client"
        )
        (
            Path(self.root_directory) / "mnt" / "onboard" / ".adds" / "nm" / "doc"
        ).write_text(self._nickelmenu_config())

    def generate(self, token: str) -> Path:
        config_path = (
            Path(self.root_directory)
            / "mnt"
            / "onboard"
            / "kosync"
            / ".kosyncConfig.json"
        )

        config_path.parent.mkdir(exist_ok=True)

        config_path.write_text(
            json.dumps(
                {
                    "Token": token,
                    "BooksDirectory": "/mnt/onboard/kosync/",
                    "Endpoint": "https://books.guus.tech/",
                }
            )
        )

        path = Path(self.root_directory) / "generated" / token / "KoboRoot.tgz"
        path.parent.mkdir(exist_ok=True, parents=True)

        with tarfile.open(path, mode="w:gz") as tar_file:
            for subdir in ["usr", "mnt"]:
                tar_file.add(
                    name=Path(self.root_directory) / subdir,
                    arcname=subdir,
                )

        config_path.unlink()

        return path


def get_client_generator(request: Request) -> ClientGenerator:
    if hasattr(request.app.state, "client_generator"):
        return request.app.state.client_generator

    raise ValueError(
        "client_generator was not found on the app, did the lifecycle event fire?"
    )
