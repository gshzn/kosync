import functools
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./kosync.db"

    upload_dir: str = "./uploads"

    base_url: str = "http://localhost:8000"

    allowed_origins: list[str] = ["http://localhost"]

    client_path: str = "./kosync_client"


@functools.cache
def get_settings() -> Settings:
    return Settings()
