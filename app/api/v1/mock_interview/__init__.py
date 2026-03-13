from fastapi import APIRouter

from .mock_interview import router
from .asr import router as asr_router
from .tts import router as tts_router

mock_interview_router = APIRouter()
mock_interview_router.include_router(router, tags=["模拟面试模块"])
mock_interview_router.include_router(asr_router, tags=["语音识别模块"])
mock_interview_router.include_router(tts_router, tags=["语音合成模块"])

__all__ = ["mock_interview_router"]
