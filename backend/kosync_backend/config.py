import functools
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./kosync.db"

    # JWT
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File uploads
    upload_dir: str = "./uploads"
    max_file_size: int = 50000000  # 50MB

    # CORS
    allowed_origins: list[str] = ["http://localhost"]


@functools.cache
def get_settings() -> Settings:
    return Settings()
