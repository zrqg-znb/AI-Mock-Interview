from fastapi import APIRouter

from .positions import router

positions_router = APIRouter()
positions_router.include_router(router, tags=["岗位模块"])

__all__ = ["positions_router"]
