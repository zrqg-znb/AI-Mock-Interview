from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.candidate import candidate_controller
from app.controllers.report import report_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import CandidateSelfUpsert
from app.services.mock_interview import mock_interview_service

router = APIRouter(dependencies=[DependAuth])


@router.get('/profile', summary='查看我的候选人档案')
async def get_my_profile():
    user_id = CTX_USER_ID.get()
    candidate = await candidate_controller.get_by_user_id(user_id)
    data = await candidate_controller.serialize(candidate) if candidate else None
    return Success(data=data)


@router.post('/profile', summary='保存我的候选人档案')
async def save_my_profile(payload: CandidateSelfUpsert):
    user_id = CTX_USER_ID.get()
    candidate = await candidate_controller.upsert_self_profile(user_id=user_id, obj_in=payload)
    return Success(data=await candidate_controller.serialize(candidate), msg='Updated Successfully')


@router.get('/dashboard', summary='查看候选人门户工作台')
async def get_candidate_dashboard():
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.get_dashboard(user_id=user_id)
    return Success(data=data)


@router.get('/reports', summary='查看我的报告列表')
async def get_my_reports(page: int = Query(1, description='页码'), page_size: int = Query(10, description='每页数量')):
    user_id = CTX_USER_ID.get()
    candidate = await candidate_controller.get_by_user_id(user_id)
    if not candidate:
        return SuccessExtra(data=[], total=0, page=page, page_size=page_size)
    total, report_objs = await report_controller.list(
        page=page,
        page_size=page_size,
        search=Q(candidate_id=candidate.id),
        order=['-created_at'],
    )
    data = [await report_controller.serialize(obj) for obj in report_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)
