from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.api.v1.router import api_router
from app.api.websocket.handlers import websocket_endpoint
from app.core.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
    os.makedirs(settings.OUTPUTS_PATH, exist_ok=True)
    os.makedirs(settings.PREVIEWS_PATH, exist_ok=True)

    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

if os.path.exists(settings.STORAGE_PATH):
    app.mount(
        "/storage",
        StaticFiles(directory=settings.STORAGE_PATH),
        name="storage"
    )

app.add_api_websocket_route("/ws/jobs/{job_id}", websocket_endpoint)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "docs": "/docs"
    }
