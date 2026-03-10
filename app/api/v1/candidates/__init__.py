from fastapi import APIRouter

from .candidates import router

candidates_router = APIRouter()
candidates_router.include_router(router, tags=["候选人模块"])

__all__ = ["candidates_router"]
