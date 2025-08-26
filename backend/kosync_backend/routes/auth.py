from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from kosync_backend.database import get_db, User
from kosync_backend.schemas import UserCreate, User as UserSchema, Token
from kosync_backend.auth import (
    authenticate_user,
    get_current_user,
    get_password_hash,
)
from kosync_backend.routes.base import templates

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/register")
def register_view(request: Request) -> Response:
    return templates.TemplatesResponse(
        request=request, name="signup.html"
    )


@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/login")
def login_view(request: Request) -> Response:
    return templates.TemplatesResponse(
        request=request, name="login.html"
    )


@router.post("/login", response_model=Token)
def token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: Annotated[Session, Depends(get_db)],
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplatesResponse(
            request=request, 
            name="login.html",
            context={"incorrect": True},
        )

    response
    return {"access_token": user.access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
