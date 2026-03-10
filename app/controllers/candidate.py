from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.admin import User
from app.models.interview import CandidateProfile, InterviewReport, InterviewSession
from app.schemas.interviews import CandidateCreate, CandidateSelfUpsert, CandidateUpdate


class CandidateController(CRUDBase[CandidateProfile, CandidateCreate, CandidateUpdate]):
    def __init__(self):
        super().__init__(model=CandidateProfile)

    async def get_by_user_id(self, user_id: int):
        return await self.model.filter(user_id=user_id).first()

    async def _validate_user(self, user_id: int, exclude_id: int | None = None):
        user = await User.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="关联用户不存在")
        query = self.model.filter(user_id=user_id)
        if exclude_id is not None:
            query = query.exclude(id=exclude_id)
        if await query.exists():
            raise HTTPException(status_code=400, detail="该用户已绑定候选人档案")
        return user

    async def create_candidate(self, obj_in: CandidateCreate):
        await self._validate_user(obj_in.user_id)
        return await self.create(obj_in)

    async def update_candidate(self, obj_in: CandidateUpdate):
        await self._validate_user(obj_in.user_id, exclude_id=obj_in.id)
        return await self.update(id=obj_in.id, obj_in=obj_in)

    async def upsert_self_profile(self, user_id: int, obj_in: CandidateSelfUpsert):
        user = await User.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        current = await self.get_by_user_id(user_id)
        payload = obj_in.model_dump()
        if current:
            return await self.update(id=current.id, obj_in=payload)
        return await self.create({"user_id": user_id, **payload})

    async def serialize(self, obj: CandidateProfile):
        data = await obj.to_dict()
        user = await User.filter(id=obj.user_id).first()
        data["user"] = await user.to_dict(exclude_fields=["password"]) if user else {}
        data["interview_count"] = await InterviewSession.filter(candidate_id=obj.id).count()
        data["report_count"] = await InterviewReport.filter(candidate_id=obj.id).count()
        return data


candidate_controller = CandidateController()
