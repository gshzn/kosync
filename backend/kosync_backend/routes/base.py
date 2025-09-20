from pathlib import Path
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="")

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/")
def index():
    return RedirectResponse("/books")


@router.get("/health")
def health_check():
    return {"status": "healthy"}
