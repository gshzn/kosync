import functools
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./kosync.db"

    # File uploads
    upload_dir: str = "./uploads"

    # CORS
    allowed_origins: list[str] = ["http://localhost"]


@functools.cache
def get_settings() -> Settings:
    return Settings()
