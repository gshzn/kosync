import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session

from kosync_backend.database import get_db, Book
from kosync_backend.schemas import Book as BookSchema, BookWithCover
from kosync_backend.epub import (
    extract_epub_metadata,
    extract_epub_cover,
    image_to_base64,
)
from kosync_backend.config import get_settings
from kosync_backend.routes.base import templates

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookSchema)
async def upload_book(
    request: Request,
    file: UploadFile = File(...),
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

    # Save file to disk
    upload_dir = get_settings().upload_dir 
    os.makedirs(upload_dir, exist_ok=True)

    book_id = uuid4()
    file_path = Path(upload_dir) / (file_path_from_storage_root := f"{book_id}.epub")
    file_path.write_bytes(content)

    try:
        book_metadata = extract_epub_metadata(file_path)

        cover_data = extract_epub_cover(file_path)

        db_book = Book(
            id=book_id,
            title=book_metadata.title,
            author=book_metadata.author,
            publisher=book_metadata.publisher,
            isbn=book_metadata.isbn,
            language=book_metadata.language,
            description=book_metadata.description,
            cover_image=cover_data,
            file_path=file_path_from_storage_root,
            file_size=file_size,
        )

        db.add(db_book)
        db.commit()

        return render_books_page(
            db, request
        ) 
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process EPUB file: {str(e)}",
        )

def render_books_page(db: Session, request: Request) -> "templates.TemplateResponse":
    books = db.query(Book).all()

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
            "cover_image_base64": image_to_base64(book.cover_image)
            if book.cover_image
            else None,
        }
        books_with_covers.append(BookWithCover(**book_dict))

    return templates.TemplateResponse(
        request=request, 
        name="index.html",
        context={"books": books_with_covers}
    )


@router.get("")
def get_user_books(
    request: Request,
    db: Session = Depends(get_db),
):
    return render_books_page(db, request)


@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
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
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
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
