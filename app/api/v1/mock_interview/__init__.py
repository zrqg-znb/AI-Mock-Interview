from fastapi import APIRouter

from .mock_interview import router
from .asr import router as asr_router

mock_interview_router = APIRouter()
mock_interview_router.include_router(router, tags=["模拟面试模块"])
mock_interview_router.include_router(asr_router, tags=["语音识别模块"])

__all__ = ["mock_interview_router"]
