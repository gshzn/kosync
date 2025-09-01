from pydantic import UUID4, BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


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


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: UUID4
    file_size: Optional[int] = None
    upload_date: datetime

    model_config = ConfigDict(from_attributes=True)


class BookWithCover(Book):
    cover_image_base64: Optional[str] = None
