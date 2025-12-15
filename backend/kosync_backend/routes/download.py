from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from kosync_backend.client_generator import ClientGenerator, get_client_generator

router = APIRouter(prefix="/download")


@router.get("")
def download(
    client_generator: Annotated[ClientGenerator, Depends(get_client_generator)],
) -> FileResponse:
    return FileResponse(path=client_generator.generate("foo"), filename="KoboRoot.tgz")
