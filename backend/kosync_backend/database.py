import contextlib
from typing import Annotated
import uuid
from fastapi import Depends, FastAPI
from sqlalchemy import (
    Engine,
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    LargeBinary,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from collections.abc import Generator

from kosync_backend.config import Settings, get_settings

Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def initialise_db(settings: Settings) -> Generator[None]:
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    access_token = Column(String, index=True, default=lambda: uuid.uuid4().hex)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    books = relationship("Book", back_populates="owner")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
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

    # Foreign key to User
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="books")
