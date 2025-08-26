from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="")

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )


@router.get("/health")
def health_check():
    return {"status": "healthy"}
