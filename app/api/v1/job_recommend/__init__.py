from fastapi import APIRouter

from .job_recommend import router

job_recommend_router = APIRouter()
job_recommend_router.include_router(router, tags=["岗位推荐模块"])

__all__ = ["job_recommend_router"]
