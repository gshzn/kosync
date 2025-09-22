import ftplib
import os
from pathlib import Path
import subprocess

def compile() -> Path:
    env = os.environ.copy()
    env.update({"GOOS": "linux", "GOARCH": "arm"})
    return_code = subprocess.call(
        args=["/usr/local/go/bin/go", "build", "-o", "dist/kosync_client"], 
        env=env,
    )

    if return_code != 0:
        raise Exception(f"Failed to compile, got status code {return_code}")

    return Path(__file__).parent / "dist" / "kosync_client"


def move_file_with_ftp(file: Path) -> None:
    ftp = ftplib.FTP()
    ftp.connect("10.0.0.7", 1021)
    ftp.login("admin", "admin")

    ftp.delete(file.name)
    with file.open('rb') as fp:
        # Command for Uploading the file "STOR filename"
        response = ftp.storbinary(f"STOR {file.name}", fp)

    print(f"FTP Transfer returned: '{response}'")


def main() -> None:
    move_file_with_ftp(compile())


if __name__ == "__main__":
    main()