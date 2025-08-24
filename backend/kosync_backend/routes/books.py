import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from kosync_backend.database import get_db, User, Book
from kosync_backend.schemas import Book as BookSchema, BookWithCover
from kosync_backend.auth import get_current_user
from kosync_backend.epub import (
    extract_epub_metadata,
    extract_epub_cover,
    image_to_base64,
)
from kosync_backend.config import get_settings

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/upload", response_model=BookSchema)
async def upload_book(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file type
    if not file.filename.lower().endswith(".epub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only EPUB files are allowed",
        )

    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > get_settings().max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

    # Save file to disk
    user_upload_dir = os.path.join(get_settings().upload_dir, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    file_path = os.path.join(user_upload_dir, file.filename)

    # If file already exists, add a number suffix
    counter = 1
    original_file_path = file_path
    while os.path.exists(file_path):
        name, ext = os.path.splitext(original_file_path)
        file_path = f"{name}_{counter}{ext}"
        counter += 1

    # Write file
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Extract metadata
        book_metadata = extract_epub_metadata(file_path)

        # Extract cover image
        cover_data = extract_epub_cover(file_path)

        # Create book record
        db_book = Book(
            title=book_metadata.title,
            author=book_metadata.author,
            publisher=book_metadata.publisher,
            isbn=book_metadata.isbn,
            language=book_metadata.language,
            description=book_metadata.description,
            cover_image=cover_data,
            file_path=file_path,
            file_size=file_size,
            owner_id=current_user.id,
        )

        db.add(db_book)
        db.commit()
        db.refresh(db_book)

        return db_book

    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process EPUB file: {str(e)}",
        )


@router.get("/", response_model=List[BookWithCover])
def get_user_books(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    books = db.query(Book).filter(Book.owner_id == current_user.id).all()

    # Convert books with cover images to base64
    books_with_covers = []
    for book in books:
        book_dict = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "isbn": book.isbn,
            "language": book.language,
            "description": book.description,
            "file_size": book.file_size,
            "upload_date": book.upload_date,
            "owner_id": book.owner_id,
            "cover_image_base64": image_to_base64(book.cover_image)
            if book.cover_image
            else None,
        }
        books_with_covers.append(BookWithCover(**book_dict))

    return books_with_covers


@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id, Book.owner_id == current_user.id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    # Delete file from disk
    if os.path.exists(book.file_path):
        os.remove(book.file_path)

    # Delete from database
    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}


@router.get("/{book_id}", response_model=BookWithCover)
def get_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id, Book.owner_id == current_user.id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    book_dict = {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "publisher": book.publisher,
        "isbn": book.isbn,
        "language": book.language,
        "description": book.description,
        "file_size": book.file_size,
        "upload_date": book.upload_date,
        "owner_id": book.owner_id,
        "cover_image_base64": image_to_base64(book.cover_image)
        if book.cover_image
        else None,
    }

    return BookWithCover(**book_dict)
