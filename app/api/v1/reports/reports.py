from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.report import report_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.interviews import InterviewReportCreate, InterviewReportUpdate

router = APIRouter()


@router.get('/list', summary='查看面试报告列表')
async def list_report(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    candidate_id: int | None = Query(None, description='候选人ID'),
    position_id: int | None = Query(None, description='岗位ID'),
    archive_status: str = Query('', description='归档状态'),
):
    q = Q()
    if candidate_id is not None:
        q &= Q(candidate_id=candidate_id)
    if position_id is not None:
        q &= Q(position_id=position_id)
    if archive_status:
        q &= Q(archive_status=archive_status)
    total, report_objs = await report_controller.list(page=page, page_size=page_size, search=q, order=['-created_at'])
    data = [await report_controller.serialize(obj) for obj in report_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看面试报告')
async def get_report(report_id: int = Query(..., description='报告ID')):
    report = await report_controller.get(id=report_id)
    return Success(data=await report_controller.serialize(report))


@router.post('/create', summary='创建面试报告')
async def create_report(report_in: InterviewReportCreate):
    await report_controller.create_report(report_in)
    return Success(msg='Created Successfully')


@router.post('/update', summary='更新面试报告')
async def update_report(report_in: InterviewReportUpdate):
    await report_controller.update_report(report_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除面试报告')
async def delete_report(report_id: int = Query(..., description='报告ID')):
    await report_controller.remove(id=report_id)
    return Success(msg='Deleted Successfully')
