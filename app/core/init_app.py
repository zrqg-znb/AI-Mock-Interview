import shutil

from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.log import logger
from app.models.admin import Api, Menu, Role
from app.schemas.menus import MenuType
from app.settings.config import settings

from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/api/v1/base/access_token",
                "/docs",
                "/openapi.json",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


def register_routers(app: FastAPI, prefix: str = "/api"):
    app.include_router(api_router, prefix=prefix)


async def init_superuser():
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password="123456",
                is_active=True,
                is_superuser=True,
            )
        )


async def upsert_menu(**payload):
    menu = await Menu.filter(path=payload["path"], parent_id=payload["parent_id"]).first()
    if menu:
        menu.update_from_dict(payload)
        await menu.save()
        return menu
    return await Menu.create(**payload)


async def init_menus():
    system_menu = await upsert_menu(
        menu_type=MenuType.CATALOG,
        name="系统管理",
        path="/system",
        order=1,
        parent_id=0,
        icon="carbon:gui-management",
        is_hidden=False,
        component="Layout",
        keepalive=False,
        redirect="/system/user",
    )
    system_children = [
        dict(
            menu_type=MenuType.MENU,
            name="用户管理",
            path="user",
            order=1,
            parent_id=system_menu.id,
            icon="material-symbols:person-outline-rounded",
            is_hidden=False,
            component="/system/user",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="角色管理",
            path="role",
            order=2,
            parent_id=system_menu.id,
            icon="carbon:user-role",
            is_hidden=False,
            component="/system/role",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="菜单管理",
            path="menu",
            order=3,
            parent_id=system_menu.id,
            icon="material-symbols:list-alt-outline",
            is_hidden=False,
            component="/system/menu",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="API管理",
            path="api",
            order=4,
            parent_id=system_menu.id,
            icon="ant-design:api-outlined",
            is_hidden=False,
            component="/system/api",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="部门管理",
            path="dept",
            order=5,
            parent_id=system_menu.id,
            icon="mingcute:department-line",
            is_hidden=False,
            component="/system/dept",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="审计日志",
            path="auditlog",
            order=6,
            parent_id=system_menu.id,
            icon="ph:clipboard-text-bold",
            is_hidden=False,
            component="/system/auditlog",
            keepalive=False,
            redirect="",
        ),
    ]
    for item in system_children:
        await upsert_menu(**item)

    await upsert_menu(
        menu_type=MenuType.MENU,
        name="一级菜单",
        path="/top-menu",
        order=2,
        parent_id=0,
        icon="material-symbols:featured-play-list-outline",
        is_hidden=False,
        component="/top-menu",
        keepalive=False,
        redirect="",
    )

    interview_menu = await upsert_menu(
        menu_type=MenuType.CATALOG,
        name="AI面试运营",
        path="/interview-admin",
        order=3,
        parent_id=0,
        icon="hugeicons:artificial-intelligence-04",
        is_hidden=False,
        component="Layout",
        keepalive=False,
        redirect="/interview-admin/candidate",
    )
    interview_children = [
        dict(
            menu_type=MenuType.MENU,
            name="候选人管理",
            path="candidate",
            order=1,
            parent_id=interview_menu.id,
            icon="solar:user-id-bold-duotone",
            is_hidden=False,
            component="/interview-admin/candidate",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="面试岗位管理",
            path="position",
            order=2,
            parent_id=interview_menu.id,
            icon="streamline:ai-industry-spark-solid",
            is_hidden=False,
            component="/interview-admin/position",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="岗位JD管理",
            path="jd",
            order=3,
            parent_id=interview_menu.id,
            icon="ph:file-text-duotone",
            is_hidden=False,
            component="/interview-admin/jd",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="面试场次管理",
            path="interview",
            order=4,
            parent_id=interview_menu.id,
            icon="mdi:head-question-outline",
            is_hidden=False,
            component="/interview-admin/interview",
            keepalive=False,
            redirect="",
        ),
        dict(
            menu_type=MenuType.MENU,
            name="面试报告档案",
            path="report",
            order=5,
            parent_id=interview_menu.id,
            icon="solar:chart-square-bold-duotone",
            is_hidden=False,
            component="/interview-admin/report",
            keepalive=False,
            redirect="",
        ),
    ]
    for item in interview_children:
        await upsert_menu(**item)


async def init_apis():
    await api_controller.refresh_api()


async def init_db():
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        await command.init_db(safe=True)
    except FileExistsError:
        pass

    await command.init()
    try:
        await command.migrate()
    except AttributeError:
        logger.warning("unable to retrieve model history from database, model history will be created from scratch")
        shutil.rmtree("migrations")
        await command.init_db(safe=True)

    await command.upgrade(run_in_transaction=True)


async def ensure_role(name: str, desc: str):
    role = await Role.filter(name=name).first()
    if role:
        role.desc = desc
        await role.save()
        return role
    return await Role.create(name=name, desc=desc)


async def init_roles():
    admin_role = await ensure_role("管理员", "管理员角色")
    await ensure_role("普通用户", "普通用户角色")
    await ensure_role("候选人", "候选人门户角色")

    all_apis = await Api.all()
    all_menus = await Menu.all()
    await admin_role.apis.clear()
    if all_apis:
        await admin_role.apis.add(*all_apis)
    await admin_role.menus.clear()
    if all_menus:
        await admin_role.menus.add(*all_menus)


async def init_data():
    await init_db()
    await init_superuser()
    await init_menus()
    await init_apis()
    await init_roles()
