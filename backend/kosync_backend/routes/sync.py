from fastapi import APIRouter, Depends
from pydantic import BaseModel, RootModel, UUID4
from sqlalchemy.orm import Session

from backend.kosync_backend.database import Book, get_db


router = APIRouter(prefix="/api/v1/sync")


SynchroniseRequest = RootModel[list[UUID4]]


class BookToSynchronise(BaseModel):
    id: UUID4
    url: str


SynchroniseResponse = RootModel[list[BookToSynchronise]]


@router.post("", response_model=SynchroniseResponse)
async def synchronise(
    request: SynchroniseRequest,
    db: Session = Depends(get_db),
) -> SynchroniseResponse:
    """Given the list of ebooks on the client, determine which new books should be downloaded."""
    available_books = db.query(Book).all()

    missing_books = set(b.id for b in available_books) - set(request.root)

    if len(missing_books) == 0:
        return SynchroniseResponse([])

    missing_books = [b for b in available_books if b.id in missing_books]

    return SynchroniseResponse(
        [BookToSynchronise(id=book.id, url=book.file_path) for book in missing_books]
    )
