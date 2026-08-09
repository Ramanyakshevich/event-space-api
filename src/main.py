from fastapi import FastAPI

from src.api.v1.router import api_v1_router
from src.core.config import settings

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.VERSION,
    debug = settings.DEBUG
)

app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }