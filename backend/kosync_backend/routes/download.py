from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="download")

@router.get("")
def download() -> FileResponse:
    # get nickeldbus
    pass