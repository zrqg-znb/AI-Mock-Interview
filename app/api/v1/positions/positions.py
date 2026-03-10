from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.position import position_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import InterviewPositionCreate, InterviewPositionUpdate

router = APIRouter()


@router.get('/list', summary='查看岗位列表')
async def list_position(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    keyword: str = Query('', description='关键词'),
    status: str = Query('', description='状态'),
    difficulty: str = Query('', description='难度'),
    is_recommended: bool | None = Query(None, description='是否推荐'),
):
    q = Q()
    if keyword:
        q &= (Q(title__contains=keyword) | Q(category__contains=keyword) | Q(department__contains=keyword))
    if status:
        q &= Q(status=status)
    if difficulty:
        q &= Q(difficulty=difficulty)
    if is_recommended is not None:
        q &= Q(is_recommended=is_recommended)
    total, position_objs = await position_controller.list(page=page, page_size=page_size, search=q, order=['-updated_at'])
    data = [await position_controller.serialize(obj) for obj in position_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看岗位')
async def get_position(position_id: int = Query(..., description='岗位ID')):
    position = await position_controller.get(id=position_id)
    return Success(data=await position_controller.serialize(position))


@router.post('/create', summary='创建岗位')
async def create_position(position_in: InterviewPositionCreate):
    await position_controller.create_position(position_in)
    return Success(msg='Created Successfully')


@router.post('/update', summary='更新岗位')
async def update_position(position_in: InterviewPositionUpdate):
    await position_controller.update_position(position_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除岗位')
async def delete_position(position_id: int = Query(..., description='岗位ID')):
    await position_controller.remove(id=position_id)
    return Success(msg='Deleted Successfully')
