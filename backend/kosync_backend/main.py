from collections.abc import AsyncGenerator
import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kosync_backend.routes import auth, base, books
from kosync_backend.database import initialise_db
from kosync_backend.config import get_settings


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    initialise_db(get_settings())
    yield


def get_app() -> FastAPI:
    app = FastAPI(
        title="KoSync API",
        description="EPUB management and synchronization API",
        version="0.1.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(base.router)

    return app


