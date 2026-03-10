from fastapi import APIRouter

from .interviews import router

interviews_router = APIRouter()
interviews_router.include_router(router, tags=["面试场次模块"])

__all__ = ["interviews_router"]
