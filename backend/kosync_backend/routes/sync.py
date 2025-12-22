from typing import Annotated
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, RootModel, UUID4
from sqlalchemy.orm import Session

from kosync_backend.database import Book, get_db
from kosync_backend.config import Settings
from kosync_backend.config import get_settings
from kosync_backend.user_middleware import get_current_user_from_id
from supabase_auth import User as SupabaseUser

router = APIRouter(prefix="/sync")


SynchroniseRequest = RootModel[list[UUID4]]


class BookToSynchronise(BaseModel):
    id: UUID4
    url: str


SynchroniseResponse = RootModel[list[BookToSynchronise]]


@router.post("/", response_model=SynchroniseResponse)
async def synchronise(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[SupabaseUser, Depends(get_current_user_from_id)],
    request: SynchroniseRequest = SynchroniseRequest([]),
) -> SynchroniseResponse:
    """Given the list of ebooks on the client, determine which new books should be downloaded."""
    available_books = db.query(Book).filter(Book.user_id == UUID(user.id)).all()

    missing_books = set(str(b.id) for b in available_books) - set(
        str(b) for b in request.root
    )

    if len(missing_books) == 0:
        return SynchroniseResponse([])

    missing_books = [b for b in available_books if str(b.id) in missing_books]

    return SynchroniseResponse(
        [
            BookToSynchronise(
                id=book.id,
                url=f"{settings.base_url.rstrip('/')}/api/v1/sync/books/{book.id}/download",
            )
            for book in missing_books
        ]
    )


@router.get("/books/{book_id}/download")
async def download(
    book_id: UUID4,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[SupabaseUser, Depends(get_current_user_from_id)],
) -> Response:
    book = (
        db.query(Book).filter(Book.id == book_id, Book.user_id == UUID(user.id)).first()
    )

    if book is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    path = Path(settings.upload_dir) / book.file_path

    return FileResponse(path)
