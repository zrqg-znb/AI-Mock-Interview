from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.interview import CandidateProfile, InterviewPosition, InterviewReport, InterviewSession
from app.schemas.interviews import InterviewReportCreate, InterviewReportUpdate


class ReportController(CRUDBase[InterviewReport, InterviewReportCreate, InterviewReportUpdate]):
    def __init__(self):
        super().__init__(model=InterviewReport)

    async def get_by_session_id(self, session_id: int):
        return await self.model.filter(session_id=session_id).first()

    async def _validate_relations(self, session_id: int, candidate_id: int, position_id: int):
        session = await InterviewSession.filter(id=session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="面试场次不存在")
        candidate = await CandidateProfile.filter(id=candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="候选人档案不存在")
        position = await InterviewPosition.filter(id=position_id).first()
        if not position:
            raise HTTPException(status_code=404, detail="岗位不存在")
        return session, candidate, position

    async def create_report(self, obj_in: InterviewReportCreate):
        await self._validate_relations(obj_in.session_id, obj_in.candidate_id, obj_in.position_id)
        if await self.model.filter(session_id=obj_in.session_id).exists():
            raise HTTPException(status_code=400, detail="该面试场次已存在报告")
        return await self.create(obj_in)

    async def update_report(self, obj_in: InterviewReportUpdate):
        return await self.update(id=obj_in.id, obj_in=obj_in)

    async def upsert_by_session(self, session: InterviewSession, payload: dict):
        current = await self.get_by_session_id(session.id)
        if current:
            await self.update(id=current.id, obj_in=payload)
            return await self.get(id=current.id)
        return await self.create(
            {
                "session_id": session.id,
                "candidate_id": session.candidate_id,
                "position_id": session.position_id,
                **payload,
            }
        )

    async def serialize(self, obj: InterviewReport):
        data = await obj.to_dict()
        session = await InterviewSession.filter(id=obj.session_id).first()
        candidate = await CandidateProfile.filter(id=obj.candidate_id).first()
        position = await InterviewPosition.filter(id=obj.position_id).first()
        data["session"] = await session.to_dict() if session else {}
        data["candidate"] = await candidate.to_dict() if candidate else {}
        data["position"] = await position.to_dict() if position else {}
        return data


report_controller = ReportController()
