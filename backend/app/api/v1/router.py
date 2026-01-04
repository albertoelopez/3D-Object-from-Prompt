from fastapi import APIRouter

from app.api.v1.endpoints import generate, jobs, prompts, download, health

api_router = APIRouter()

api_router.include_router(generate.router)
api_router.include_router(jobs.router)
api_router.include_router(prompts.router)
api_router.include_router(download.router)
api_router.include_router(health.router)
