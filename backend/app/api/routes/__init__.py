from fastapi import APIRouter

from app.api.routes import admin, candidates, dashboard, decisions, documents, jobs

api_router = APIRouter()

api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(candidates.router, tags=["candidates"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(decisions.router, tags=["decisions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
