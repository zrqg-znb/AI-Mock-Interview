from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.candidate import candidate_controller
from app.models.admin import User
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import CandidateCreate, CandidateUpdate

router = APIRouter()


@router.get('/list', summary='查看候选人列表')
async def list_candidate(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    username: str = Query('', description='用户名'),
    target_position: str = Query('', description='目标岗位'),
    job_status: str = Query('', description='求职状态'),
    is_active: bool | None = Query(None, description='是否启用'),
):
    q = Q()
    if target_position:
        q &= Q(target_position__contains=target_position)
    if job_status:
        q &= Q(job_status=job_status)
    if is_active is not None:
        q &= Q(is_active=is_active)
    if username:
        user_ids = await User.filter(Q(username__contains=username) | Q(email__contains=username)).values_list('id', flat=True)
        if not user_ids:
            return SuccessExtra(data=[], total=0, page=page, page_size=page_size)
        q &= Q(user_id__in=list(user_ids))
    total, candidate_objs = await candidate_controller.list(page=page, page_size=page_size, search=q, order=['-updated_at'])
    data = [await candidate_controller.serialize(obj) for obj in candidate_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看候选人')
async def get_candidate(candidate_id: int = Query(..., description='候选人ID')):
    candidate = await candidate_controller.get(id=candidate_id)
    return Success(data=await candidate_controller.serialize(candidate))


@router.post('/create', summary='创建候选人')
async def create_candidate(candidate_in: CandidateCreate):
    await candidate_controller.create_candidate(candidate_in)
    return Success(msg='Created Successfully')


@router.post('/update', summary='更新候选人')
async def update_candidate(candidate_in: CandidateUpdate):
    await candidate_controller.update_candidate(candidate_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除候选人')
async def delete_candidate(candidate_id: int = Query(..., description='候选人ID')):
    await candidate_controller.remove(id=candidate_id)
    return Success(msg='Deleted Successfully')
