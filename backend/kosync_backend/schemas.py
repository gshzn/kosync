from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


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
    id: int
    file_size: Optional[int] = None
    upload_date: datetime
    owner_id: int

    class Config:
        from_attributes = True


class BookWithCover(Book):
    cover_image_base64: Optional[str] = None
