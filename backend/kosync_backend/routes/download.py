from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from supabase_auth import User as SupabaseUser

from kosync_backend.client_generator import ClientGenerator, get_client_generator
from kosync_backend.user_middleware import get_current_user_from_jwt

router = APIRouter(prefix="/download")


@router.get("")
def download(
    client_generator: Annotated[ClientGenerator, Depends(get_client_generator)],
    user: Annotated[SupabaseUser, Depends(get_current_user_from_jwt)],
) -> FileResponse:
    return FileResponse(
        path=client_generator.generate(user.id), filename="KoboRoot.tgz"
    )
