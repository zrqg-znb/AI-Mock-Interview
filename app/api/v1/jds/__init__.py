from fastapi import APIRouter

from .jds import router

jds_router = APIRouter()
jds_router.include_router(router, tags=["JD模块"])

__all__ = ["jds_router"]
