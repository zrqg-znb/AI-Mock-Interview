from fastapi import APIRouter

from app.core.dependency import DependPermission

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .candidate_portal import candidate_portal_router
from .candidates import candidates_router
from .depts import depts_router
from .interviews import interviews_router
from .jds import jds_router
from .job_recommend import job_recommend_router
from .menus import menus_router
from .mock_interview import mock_interview_router
from .positions import positions_router
from .reports import reports_router
from .roles import roles_router
from .users import users_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(candidate_portal_router, prefix="/candidate_portal")
v1_router.include_router(job_recommend_router, prefix="/job_recommend")
v1_router.include_router(mock_interview_router, prefix="/mock_interview")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermission])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermission])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermission])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermission])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermission])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermission])
v1_router.include_router(candidates_router, prefix="/candidate", dependencies=[DependPermission])
v1_router.include_router(positions_router, prefix="/position", dependencies=[DependPermission])
v1_router.include_router(jds_router, prefix="/jd", dependencies=[DependPermission])
v1_router.include_router(interviews_router, prefix="/interview", dependencies=[DependPermission])
v1_router.include_router(reports_router, prefix="/report", dependencies=[DependPermission])
