from datetime import datetime

from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.interview import CandidateProfile, InterviewPosition, InterviewReport, InterviewSession, InterviewTurn, PositionJD
from app.schemas.interviews import InterviewSessionCreate, InterviewSessionUpdate


class InterviewController(CRUDBase[InterviewSession, InterviewSessionCreate, InterviewSessionUpdate]):
    def __init__(self):
        super().__init__(model=InterviewSession)

    def generate_session_no(self):
        return f"MOCK{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    async def _validate_relations(self, candidate_id: int, position_id: int, jd_id: int | None = None):
        candidate = await CandidateProfile.filter(id=candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="候选人档案不存在")
        position = await InterviewPosition.filter(id=position_id).first()
        if not position:
            raise HTTPException(status_code=404, detail="岗位不存在")
        jd = None
        if jd_id is not None:
            jd = await PositionJD.filter(id=jd_id).first()
            if not jd:
                raise HTTPException(status_code=404, detail="JD 不存在")
            if jd.position_id != position_id:
                raise HTTPException(status_code=400, detail="JD 与岗位不匹配")
        return candidate, position, jd

    async def create_session(self, obj_in: InterviewSessionCreate | dict):
        payload = obj_in.copy() if isinstance(obj_in, dict) else obj_in.model_dump()
        candidate, _, _ = await self._validate_relations(payload["candidate_id"], payload["position_id"], payload.get("jd_id"))
        payload["session_no"] = payload.get("session_no") or self.generate_session_no()
        payload["user_id"] = candidate.user_id
        if payload.get("status") == "running" and payload.get("started_at") is None:
            payload["started_at"] = datetime.now()
        return await self.create(payload)

    async def update_session(self, obj_in: InterviewSessionUpdate | dict):
        current_id = obj_in["id"] if isinstance(obj_in, dict) else obj_in.id
        current = await self.get(id=current_id)
        candidate_id = obj_in.get("candidate_id") if isinstance(obj_in, dict) else obj_in.candidate_id
        candidate_id = candidate_id if candidate_id is not None else current.candidate_id
        position_id = obj_in.get("position_id") if isinstance(obj_in, dict) else obj_in.position_id
        position_id = position_id if position_id is not None else current.position_id
        jd_id = obj_in.get("jd_id") if isinstance(obj_in, dict) else obj_in.jd_id
        jd_id = jd_id if jd_id is not None else current.jd_id
        candidate, _, _ = await self._validate_relations(candidate_id, position_id, jd_id)
        payload = obj_in.copy() if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True, exclude={"id"})
        payload.pop("id", None)
        payload["user_id"] = candidate.user_id
        if payload.get("status") == "running" and payload.get("started_at") is None and current.started_at is None:
            payload["started_at"] = datetime.now()
        if payload.get("status") == "completed" and payload.get("ended_at") is None:
            payload["ended_at"] = datetime.now()
        return await self.update(id=current_id, obj_in=payload)

    async def add_turn(
        self,
        session_id: int,
        round_no: int,
        speaker: str,
        content: str,
        source: str = "segment",
        segment_index: int = 0,
    ):
        return await InterviewTurn.create(
            session_id=session_id,
            round_no=round_no,
            speaker=speaker,
            content=content,
            source=source,
            segment_index=segment_index,
        )

    async def get_turns(self, session_id: int):
        return await InterviewTurn.filter(session_id=session_id).order_by("created_at", "id")

    async def serialize_turn(self, obj: InterviewTurn):
        return await obj.to_dict()

    async def serialize(self, obj: InterviewSession, include_turns: bool = False):
        data = await obj.to_dict()
        candidate = await CandidateProfile.filter(id=obj.candidate_id).first()
        position = await InterviewPosition.filter(id=obj.position_id).first()
        jd = await PositionJD.filter(id=obj.jd_id).first() if obj.jd_id else None
        report = await InterviewReport.filter(session_id=obj.id).first()
        data["candidate"] = await candidate.to_dict() if candidate else {}
        data["position"] = await position.to_dict() if position else {}
        data["jd"] = await jd.to_dict() if jd else {}
        data["report_id"] = report.id if report else None
        data["turn_count"] = await InterviewTurn.filter(session_id=obj.id).count()
        if include_turns:
            turns = await self.get_turns(obj.id)
            data["turns"] = [await self.serialize_turn(turn) for turn in turns]
        return data


interview_controller = InterviewController()
