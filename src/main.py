from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.v1.router import api_v1_router
from src.core.config import settings
from src.core.redis import init_redis_pool, close_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool()
    yield
    await close_redis_pool()

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.VERSION,
    lifespan=lifespan
)

app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }