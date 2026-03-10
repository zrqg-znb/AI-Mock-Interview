from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.interview import InterviewPosition, PositionJD
from app.schemas.interviews import InterviewPositionCreate, InterviewPositionUpdate


class PositionController(CRUDBase[InterviewPosition, InterviewPositionCreate, InterviewPositionUpdate]):
    def __init__(self):
        super().__init__(model=InterviewPosition)

    async def create_position(self, obj_in: InterviewPositionCreate):
        return await self.create(obj_in)

    async def update_position(self, obj_in: InterviewPositionUpdate):
        if not await self.model.filter(id=obj_in.id).exists():
            raise HTTPException(status_code=404, detail="岗位不存在")
        return await self.update(id=obj_in.id, obj_in=obj_in)

    async def serialize(self, obj: InterviewPosition):
        data = await obj.to_dict()
        active_jd = await PositionJD.filter(position_id=obj.id, is_active=True).order_by("-version").first()
        data["active_jd_id"] = active_jd.id if active_jd else None
        data["active_jd_version"] = active_jd.version if active_jd else None
        data["jd_count"] = await PositionJD.filter(position_id=obj.id).count()
        return data


position_controller = PositionController()
