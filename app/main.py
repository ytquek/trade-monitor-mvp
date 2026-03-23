from fastapi import FastAPI
from app.db.session import init_db
from app.api.routes import sources, documents, digests

app = FastAPI(title="Trade & Maritime Monitor MVP", version="0.1.0")

@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.include_router(sources.router)
app.include_router(documents.router)
app.include_router(digests.router)

@app.get("/")
def root() -> dict:
    return {
        "name": "Trade & Maritime Monitor MVP",
        "status": "ok",
        "docs": "/docs"
    }
