from collections.abc import AsyncGenerator
import contextlib
from fastapi import FastAPI

from kosync_backend.routes import auth, books
from kosync_backend.database import initialise_db
from kosync_backend.config import get_settings


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    initialise_db(get_settings())
    yield


app = FastAPI(
    title="KoSync API",
    description="EPUB management and synchronization API",
    version="0.1.0",
    lifespan=lifespan
)


# Include routers
app.include_router(auth.router)
app.include_router(books.router)


@app.get("/")
def index():
    return {"message": "Welcome to KoSync API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
