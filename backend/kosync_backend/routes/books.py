import os
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from kosync_backend.config import Settings
from kosync_backend.config import get_settings
from kosync_backend.database import Book, get_db
from kosync_backend.epub import (
    extract_epub_cover,
    extract_epub_metadata,
)
from kosync_backend.schemas import BookModel
from kosync_backend.schemas import BookUpdateRequest

router = APIRouter(prefix="/books")


@router.post("")
async def upload_book(
    request: Request,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> BookModel:
    if not file.filename or not file.filename.lower().endswith(".epub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only EPUB files are allowed",
        )

    # Check file size
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

        return BookModel.from_orm(db_book)
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process EPUB file: {str(e)}",
        )


@router.get("")
def get_user_books(
    request: Request,
    db: Session = Depends(get_db),
) -> list[BookModel]:
    books = db.query(Book).all()

    return [BookModel.from_orm(book) for book in books]


@router.delete("/{book_id}")
def delete_book(
    book_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    book = db.query(Book).filter(Book.id == book_id).first()

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

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/{book_id}", response_model=BookModel)
def get_book(
    book_id: str,
    db: Session = Depends(get_db),
) -> BookModel:
    book = db.query(Book).filter(Book.id == UUID(book_id)).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return BookModel.from_orm(book)


@router.patch("/{book_id}", response_model=BookModel)
def update_book(
    book_id: str,
    request: BookUpdateRequest,
    db: Session = Depends(get_db),
) -> BookModel:
    book = db.query(Book).where(Book.id == UUID(book_id)).first()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    book.title = request.title
    book.author = request.author
    book.description = request.description

    db.commit()

    return BookModel.from_orm(book)


@router.get("/{book_id}/download")
async def download(
    book_id: UUID,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    path = Path(settings.upload_dir) / book.file_path

    return FileResponse(path)
