from fastapi import APIRouter, Query

from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.schemas.base import Success
from app.schemas.interviews import FinishMockInterviewIn, NextInterviewQuestionIn, StartMockInterviewIn, SubmitInterviewSegmentIn
from app.services.mock_interview import mock_interview_service

router = APIRouter(dependencies=[DependAuth])


@router.post('/start', summary='开始模拟面试')
async def start_mock_interview(payload: StartMockInterviewIn):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.start_interview(
        user_id=user_id,
        position_id=payload.position_id,
        total_rounds=payload.total_rounds,
    )
    return Success(data=data)


@router.post('/submit_segment', summary='提交语音分段文本')
async def submit_segment(payload: SubmitInterviewSegmentIn):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.submit_segment(
        user_id=user_id,
        session_id=payload.session_id,
        content=payload.content,
        segment_index=payload.segment_index,
    )
    return Success(data=data)


@router.post('/next_question', summary='获取下一道面试题')
async def next_question(payload: NextInterviewQuestionIn):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.next_question(user_id=user_id, session_id=payload.session_id)
    return Success(data=data)


@router.post('/finish', summary='结束模拟面试并生成报告')
async def finish_mock_interview(payload: FinishMockInterviewIn):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.finish_interview(user_id=user_id, session_id=payload.session_id)
    return Success(data=data)


@router.get('/report', summary='获取模拟面试报告')
async def get_mock_interview_report(
    report_id: int | None = Query(None, description='报告ID'),
    session_id: int | None = Query(None, description='场次ID'),
):
    user_id = CTX_USER_ID.get()
    data = await mock_interview_service.get_report(user_id=user_id, report_id=report_id, session_id=session_id)
    return Success(data=data)
