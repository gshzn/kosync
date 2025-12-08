from collections.abc import AsyncGenerator
import contextlib

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kosync_backend.client_generator import ClientGenerator
from kosync_backend.routes import books, sync, download
from kosync_backend.database import initialise_db
from kosync_backend.config import get_settings


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    initialise_db(get_settings())
    with ClientGenerator(get_settings()) as client_generator:
        app.state.client_generator = client_generator
        yield


def get_app() -> FastAPI:
    app = FastAPI(
        title="KoSync API",
        description="EPUB management and synchronization API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    main_api_router = APIRouter(prefix="/api/v1")
    main_api_router.include_router(books.router)
    main_api_router.include_router(sync.router)
    main_api_router.include_router(download.router)

    app.include_router(router=main_api_router)

    return app
