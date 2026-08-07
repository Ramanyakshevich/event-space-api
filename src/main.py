from fastapi import FastAPI
from src.core.config import settings

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.VERSION,
    debug = settings.DEBUG
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }