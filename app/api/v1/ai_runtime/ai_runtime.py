from fastapi import APIRouter, Query

from app.schemas.base import Success
from app.services.ai_runtime import ai_runtime_service

router = APIRouter()


@router.get('/status', summary='查看 AI 运行状态')
async def get_ai_runtime_status(limit: int = Query(20, ge=1, le=50)):
    data = ai_runtime_service.get_status(limit=limit)
    return Success(data=data)


@router.post('/test', summary='执行 AI 连通测试')
async def run_ai_runtime_test():
    data = await ai_runtime_service.run_connectivity_check()
    return Success(data=data)
