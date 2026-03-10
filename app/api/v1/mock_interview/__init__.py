from fastapi import APIRouter

from .mock_interview import router

mock_interview_router = APIRouter()
mock_interview_router.include_router(router, tags=["模拟面试模块"])

__all__ = ["mock_interview_router"]
