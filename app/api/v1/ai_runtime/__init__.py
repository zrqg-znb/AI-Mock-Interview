from fastapi import APIRouter

from .ai_runtime import router

ai_runtime_router = APIRouter()
ai_runtime_router.include_router(router, tags=['AI 运行状态'])

__all__ = ['ai_runtime_router']
