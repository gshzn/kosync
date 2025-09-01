from fastapi import APIRouter, Response
from pydantic import BaseModel


router = APIRouter(prefix="/sync")


class SynchroniseRequest(BaseModel):
    pass


@router.post("")
async def synchronise() -> Response:
    """ Given the list of ebooks on the client, determine which new books should be downloaded """
