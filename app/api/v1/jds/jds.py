from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.jd import jd_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import PositionJDCreate, PositionJDUpdate

router = APIRouter()


@router.get('/list', summary='查看JD列表')
async def list_jd(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    position_id: int | None = Query(None, description='岗位ID'),
    keyword: str = Query('', description='关键词'),
    is_active: bool | None = Query(None, description='是否启用'),
):
    q = Q()
    if position_id is not None:
        q &= Q(position_id=position_id)
    if keyword:
        q &= Q(jd_text__contains=keyword)
    if is_active is not None:
        q &= Q(is_active=is_active)
    total, jd_objs = await jd_controller.list(page=page, page_size=page_size, search=q, order=['-created_at'])
    data = [await jd_controller.serialize(obj) for obj in jd_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看JD')
async def get_jd(jd_id: int = Query(..., description='JD ID')):
    jd = await jd_controller.get(id=jd_id)
    return Success(data=await jd_controller.serialize(jd))


@router.post('/create', summary='创建JD')
async def create_jd(jd_in: PositionJDCreate):
    await jd_controller.create_jd(jd_in)
    return Success(msg='Created Successfully')


@router.post('/update', summary='更新JD')
async def update_jd(jd_in: PositionJDUpdate):
    await jd_controller.update_jd(jd_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除JD')
async def delete_jd(jd_id: int = Query(..., description='JD ID')):
    await jd_controller.remove(id=jd_id)
    return Success(msg='Deleted Successfully')
