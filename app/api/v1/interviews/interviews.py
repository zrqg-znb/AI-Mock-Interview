from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.interview import interview_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import InterviewSessionCreate, InterviewSessionUpdate

router = APIRouter()


@router.get('/list', summary='查看面试场次列表')
async def list_interview(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    status: str = Query('', description='状态'),
    candidate_id: int | None = Query(None, description='候选人ID'),
    position_id: int | None = Query(None, description='岗位ID'),
):
    q = Q()
    if status:
        q &= Q(status=status)
    if candidate_id is not None:
        q &= Q(candidate_id=candidate_id)
    if position_id is not None:
        q &= Q(position_id=position_id)
    total, interview_objs = await interview_controller.list(page=page, page_size=page_size, search=q, order=['-created_at'])
    data = [await interview_controller.serialize(obj) for obj in interview_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看面试场次')
async def get_interview(interview_id: int = Query(..., description='场次ID')):
    interview = await interview_controller.get(id=interview_id)
    return Success(data=await interview_controller.serialize(interview, include_turns=True))


@router.post('/create', summary='创建面试场次')
async def create_interview(interview_in: InterviewSessionCreate):
    await interview_controller.create_session(interview_in)
    return Success(msg='Created Successfully')


@router.post('/update', summary='更新面试场次')
async def update_interview(interview_in: InterviewSessionUpdate):
    await interview_controller.update_session(interview_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除面试场次')
async def delete_interview(interview_id: int = Query(..., description='场次ID')):
    await interview_controller.remove(id=interview_id)
    return Success(msg='Deleted Successfully')
