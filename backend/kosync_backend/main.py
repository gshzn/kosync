from fastapi import FastAPI
from kosync_backend.routes import auth, books

app = FastAPI(
    title="KoSync API",
    description="EPUB management and synchronization API",
    version="0.1.0",
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
