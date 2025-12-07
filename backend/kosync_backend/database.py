from collections.abc import Generator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    UUID,
    DateTime,
    Engine,
    Integer,
    LargeBinary,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.sql import func

from kosync_backend.config import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


SessionLocal = sessionmaker(autoflush=False)


def initialise_db(settings: Settings) -> None:
    Base.metadata.create_all(bind=get_engine(settings))


def get_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url, connect_args={"check_same_thread": False}
    )


def get_db(settings: Annotated[Settings, Depends(get_settings)]) -> Generator[Session]:
    db = SessionLocal(bind=get_engine(settings))
    try:
        yield db
    finally:
        db.close()


class Book(Base):
    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String, nullable=True)
    isbn: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
