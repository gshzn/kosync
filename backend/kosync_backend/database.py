from typing import Annotated
from fastapi import Depends
from sqlalchemy import (
    UUID,
    Engine,
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    LargeBinary,
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import func
from collections.abc import Generator

from kosync_backend.config import Settings, get_settings

Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


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

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String)
    publisher = Column(String)
    isbn = Column(String)
    language = Column(String)
    description = Column(Text)
    cover_image = Column(LargeBinary)  # Store cover image as binary data
    file_path = Column(String, nullable=False)  # Path to the EPUB file
    file_size = Column(Integer)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
