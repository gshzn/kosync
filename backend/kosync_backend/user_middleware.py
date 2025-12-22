from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from supabase_auth import User as SupabaseUser
from supabase_auth.errors import AuthApiError

from kosync_backend.config import Settings, get_settings


security = HTTPBearer()


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    return credentials.credentials


def get_supabase(settings: Annotated[Settings, Depends(get_settings)]) -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


async def get_current_user_from_jwt(
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    supabase: Annotated[Client, Depends(get_supabase)],
) -> SupabaseUser:
    try:
        response = supabase.auth.get_user(bearer_token)
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return response.user


async def get_current_user_from_id(
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    supabase: Annotated[Client, Depends(get_supabase)],
) -> SupabaseUser:
    try:
        return supabase.auth.admin.get_user_by_id(bearer_token).user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid User ID format",
        )
