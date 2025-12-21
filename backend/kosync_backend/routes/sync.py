from pathlib import Path

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, RootModel, UUID4
from sqlalchemy.orm import Session

from kosync_backend.database import Book, get_db
from kosync_backend.config import Settings
from kosync_backend.config import get_settings

router = APIRouter(prefix="/sync")


SynchroniseRequest = RootModel[list[UUID4]]


class BookToSynchronise(BaseModel):
    id: UUID4
    url: str


SynchroniseResponse = RootModel[list[BookToSynchronise]]


@router.post("/", response_model=SynchroniseResponse)
async def synchronise(
    request: SynchroniseRequest = SynchroniseRequest([]),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SynchroniseResponse:
    """Given the list of ebooks on the client, determine which new books should be downloaded."""
    available_books = db.query(Book).all()

    missing_books = set(str(b.id) for b in available_books) - set(
        str(b) for b in request.root
    )

    if len(missing_books) == 0:
        return SynchroniseResponse([])

    missing_books = [b for b in available_books if str(b.id) in missing_books]

    return SynchroniseResponse(
        [
            BookToSynchronise(
                id=book.id, url=f"{settings.base_url.rstrip('/')}/api/v1/books/{book.id}/download"
            )
            for book in missing_books
        ]
    )


@router.get("/books/{book_id}/download")
async def download(
    book_id: UUID4,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    path = Path(settings.upload_dir) / book.file_path

    return FileResponse(path)
