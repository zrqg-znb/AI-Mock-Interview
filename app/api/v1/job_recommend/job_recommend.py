from fastapi import APIRouter, Query

from app.core.dependency import DependAuth
from app.core.ctx import CTX_USER_ID
from app.schemas.base import Success
from app.services.mock_interview import mock_interview_service

router = APIRouter(dependencies=[DependAuth])


@router.get('/list', summary='获取岗位推荐列表')
async def list_job_recommend(keyword: str = Query('', description='关键词'), page_size: int = Query(12, description='数量')):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.list_recommendations(user_id=user_id, page_size=page_size, keyword=keyword)
    return Success(data=data)


@router.get('/detail', summary='获取岗位推荐详情')
async def get_job_recommend_detail(position_id: int = Query(..., description='岗位ID')):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.get_position_detail(user_id=user_id, position_id=position_id)
    return Success(data=data)
