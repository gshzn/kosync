import base64
from pydantic import UUID4, BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from kosync_backend.database import Book as ORMBook


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class BookModel(BaseModel):
    id: UUID4
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    upload_date: datetime
    cover_image_base64: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_sqlalchemy_orm(cls, orm_book: ORMBook) -> "BookModel":  # type: ignore
        return cls(
            id=orm_book.id,  # type: ignore
            title=orm_book.title,
            author=orm_book.author,
            publisher=orm_book.publisher,
            isbn=orm_book.isbn,
            language=orm_book.language,
            upload_date=orm_book.upload_date,
            description=orm_book.description,
            cover_image_base64=base64.b64encode(orm_book.cover_image).decode()
            if orm_book.cover_image
            else None,
        )


class BookUpdateRequest(BaseModel):
    title: str
    author: str
    description: str
