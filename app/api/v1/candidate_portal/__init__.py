from fastapi import APIRouter

from .candidate_portal import router

candidate_portal_router = APIRouter()
candidate_portal_router.include_router(router, tags=["候选人门户模块"])

__all__ = ["candidate_portal_router"]
