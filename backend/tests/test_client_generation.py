import os
from pathlib import Path
import shutil
import tarfile
import tempfile
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from kosync_backend.client_generator import ClientGenerator
from kosync_backend.config import Settings


@pytest.fixture()
def mock_nickelmenu_download(mocker: MockerFixture) -> mock.Mock:
    kobo_root_path = Path(__file__).parent / "resources" / "nickelmenu_KoboRoot.tgz"

    return mocker.patch.object(
        ClientGenerator,
        "_download_nickelmenu",
        return_value=kobo_root_path
    )


@pytest.fixture()
def mock_nickeldbus_download(mocker: MockerFixture) -> mock.Mock:
    kobo_root_path = Path(__file__).parent / "resources" / "nickeldbus_KoboRoot.tgz"

    return mocker.patch.object(
        ClientGenerator,
        "_download_nickeldbus",
        return_value=kobo_root_path
    )


def test_client_generation_fetches_all_resources(
    mock_nickelmenu_download: mock.Mock,
    mock_nickeldbus_download: mock.Mock,
) -> None:
    with ClientGenerator(Settings()) as client_generator:
        assert mock_nickelmenu_download.called
        assert mock_nickeldbus_download.called

        root_path = Path(str(client_generator.root_directory))

        assert set(os.listdir(root_path)) == {"etc", "usr", "mnt"}

        nm_config = (
            Path(client_generator.root_directory)
            / "mnt"
            / "onboard"
            / ".adds"
            / "nm"
            / "doc"
        )

        assert "KoSync" in nm_config.read_text()
        assert (
            Path(client_generator.root_directory) / "mnt" / "onboard" / "kosync_client"
        ).exists()


def test_client_generation_generates_a_client_archive(
    mock_nickelmenu_download: mock.Mock,
    mock_nickeldbus_download: mock.Mock,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        with ClientGenerator(Settings()) as client_generator:
            assert mock_nickelmenu_download.called
            assert mock_nickeldbus_download.called

            archive_path = client_generator.generate(token := "foo")

            assert archive_path.exists()
            shutil.copy(archive_path, client_path := Path(temp_dir) / "KoboRoot.tgz")

        assert client_path.exists()
        with tarfile.open(client_path, "r:gz") as client_archive:
            client_archive.extractall(path=client_path.parent, filter="tar")

        assert (client_path.parent / "etc/dbus-1/system.d/com-github-shermp-nickeldbus.conf").exists()
        assert (client_path.parent / "mnt" / "onboard" / "kosync_client").exists()
        assert (
            "KoSync"
            in (
                client_path.parent / "mnt" / "onboard" / ".adds" / "nm" / "doc"
            ).read_text()
        )
        assert f'"Token": "{token}"' in (
            (
                client_path.parent / "mnt" / "onboard" / "kosync" / ".kosyncConfig.json"
            ).read_text()
        )
