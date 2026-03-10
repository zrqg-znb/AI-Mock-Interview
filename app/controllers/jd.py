from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.interview import InterviewPosition, PositionJD
from app.schemas.interviews import PositionJDCreate, PositionJDUpdate


class JDController(CRUDBase[PositionJD, PositionJDCreate, PositionJDUpdate]):
    def __init__(self):
        super().__init__(model=PositionJD)

    async def _validate_position(self, position_id: int):
        position = await InterviewPosition.filter(id=position_id).first()
        if not position:
            raise HTTPException(status_code=404, detail="岗位不存在")
        return position

    async def create_jd(self, obj_in: PositionJDCreate):
        await self._validate_position(obj_in.position_id)
        if await self.model.filter(position_id=obj_in.position_id, version=obj_in.version).exists():
            raise HTTPException(status_code=400, detail="该岗位下 JD 版本已存在")
        if obj_in.is_active:
            await self.model.filter(position_id=obj_in.position_id).update(is_active=False)
        return await self.create(obj_in)

    async def update_jd(self, obj_in: PositionJDUpdate):
        await self._validate_position(obj_in.position_id)
        duplicate = self.model.filter(position_id=obj_in.position_id, version=obj_in.version).exclude(id=obj_in.id)
        if await duplicate.exists():
            raise HTTPException(status_code=400, detail="该岗位下 JD 版本已存在")
        if obj_in.is_active:
            await self.model.filter(position_id=obj_in.position_id).exclude(id=obj_in.id).update(is_active=False)
        return await self.update(id=obj_in.id, obj_in=obj_in)

    async def get_active_by_position(self, position_id: int):
        return await self.model.filter(position_id=position_id, is_active=True).order_by("-version").first()

    async def serialize(self, obj: PositionJD):
        data = await obj.to_dict()
        position = await InterviewPosition.filter(id=obj.position_id).first()
        data["position"] = await position.to_dict() if position else {}
        return data


jd_controller = JDController()
