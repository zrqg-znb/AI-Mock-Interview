from fastapi import APIRouter

from .reports import router

reports_router = APIRouter()
reports_router.include_router(router, tags=["面试报告模块"])

__all__ = ["reports_router"]
