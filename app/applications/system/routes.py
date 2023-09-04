import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.applications.users.models import User
from app.core.auth.deps import get_current_active_superuser, get_access_token_data, permissions_required, get_current_active_user
from app.core.base.schemas import ResponseData
from typing import Optional

from .models import Menu, Role
from .schemas import Route, Catalog, MenuType, MenuOut, MenuIn, MenuUpdate, RoleIn, RoleOut, RoleUpdate, RoleOutList, PageQuery
logger = logging.getLogger(__name__)

router = APIRouter(tags=['system'])


@router.get("/catalogs", response_model=ResponseData[list[Catalog]], status_code=200)
async def catalogs(_=Depends(get_access_token_data)):
    data = await Menu.full_hierarchy_catalog()
    return {"data": data}


@router.get("/menus", response_model=ResponseData[list[MenuOut]], status_code=200)
async def menus(keywords: Optional[str] = None, _=Depends(get_access_token_data)):
    data = await Menu.full_hierarchy_menu(query=keywords)
    return {"data": data}


@router.post("/menus", response_model=ResponseData[int], status_code=201)
async def create_menu(menu: MenuIn, current_user: User = Depends(get_current_active_superuser)):
    parent_menu = None
    if menu.parent_id:
        parent_menu = await Menu.get(id=menu.parent_id)

    menu = Menu(**menu.model_dump(), parent=parent_menu)
    await menu.save()

    # menu = await Menu.create(**menu.model_dump())
    print(menu)
    return {"data": 0}


@router.delete("/menus/{id}", response_model=ResponseData[int], status_code=200)
async def delete_menu(id: int, current_user: User = Depends(get_current_active_superuser)):
    menu = await Menu.get(id=id)
    await menu.delete()
    return {"data": 0}


@router.get("/menus/{id}", response_model=ResponseData[MenuUpdate], status_code=200)
async def get_menu(id: int, current_user: User = Depends(get_current_active_superuser)):
    menu = await Menu.get(id=id)
    return {"data": menu}


@router.put("/menus/{id}", response_model=ResponseData[int], status_code=200)
async def update_menu(id: int, m: MenuUpdate, current_user: User = Depends(get_current_active_superuser)):
    menu = await Menu.get(id=id)
    data = m.model_dump(exclude_unset=True, exclude=["parent_id"])
    if data.get("parent_id"):
        parent_menu = await Menu.get(id=data["parent_id"])
        data["parent"] = parent_menu

    menu.update_from_dict(data)
    await menu.save()
    return {"data": 0}


@router.get("/roles", response_model=ResponseData[RoleOutList], status_code=200)
async def roles(page: Optional[int] = Query(title="page", ge=1, default=1),
                page_size: Optional[int] = Query(
                    title="page_size", le=20, default=10),
                keywords: Optional[str] = None,
                current_user: User = Depends(get_current_active_user)):
    print(page, page_size, keywords)
    query = Role.all()
    if keywords:
        query = query.filter(name__icontains=keywords)

    total = await query.count()
    items = await query.offset((page-1) * page_size).limit(page_size).all()

    return {"data": {
        "total": total,
        "items": items
    }}


@router.get("/roles/{id}/menus", response_model=ResponseData[list[int]], status_code=200)
async def get_role_menus(id: int, current_user: User = Depends(get_current_active_superuser)):
    role = await Role.filter(id=id).prefetch_related("permissions").first()
    return {"data": [m.id for m in role.permissions]}


@router.put("/roles/{id}/menus", response_model=ResponseData[int], status_code=200)
async def update_role_menus(id: int, menus: list[int], current_user: User = Depends(get_current_active_superuser)):
    role = await Role.get(id=id)
    await role.permissions.clear()
    db_menus = await Menu.filter(id__in=menus).all()
    await role.permissions.add(*db_menus)
    return {"data": 0}


@router.get("/roles/{id}", response_model=ResponseData[RoleOut], status_code=200)
async def get_role(id: int, current_user: User = Depends(get_current_active_superuser)):
    role = await Role.get(id=id)
    return {"data": role}


@router.post("/roles", response_model=ResponseData[int], status_code=201)
async def create_role(role: RoleIn, current_user: User = Depends(get_current_active_superuser)):
    role = await Role.create(**role.model_dump())
    return {"data": 0}


@router.put("/roles/{id}", response_model=ResponseData[RoleOut], status_code=200)
async def update_role(id: int, role: RoleUpdate, current_user: User = Depends(get_current_active_superuser)):
    role_db = await Role.get(id=id)
    role_db.update_from_dict(role.model_dump(exclude_unset=True))
    await role_db.save()
    return {"data": role_db}


@router.delete("/roles/{id}", response_model=ResponseData[int], status_code=200)
async def delete_role(id: str, current_user: User = Depends(get_current_active_superuser)):
    ids = id.split(",")
    ids = [int(i) for i in ids]
    await Role.filter(id__in=ids).delete()
    return {"data": 0}


@router.get("/routes", response_model=ResponseData[list[Route]],
            response_model_exclude_none=True,
            status_code=200)
async def routes(current_user: User = Depends(get_current_active_user)):
    data = [
        {
            "path": "/system",
            "component": "Layout",
            "redirect": "/system/user",
            "meta": {
                "title": "系统管理",
                "icon": "system",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "user",
                    "component": "system/user/index",
                    "name": "User",
                    "meta": {
                        "title": "用户管理",
                        "icon": "user",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "role",
                    "component": "system/role/index",
                    "name": "Role",
                    "meta": {
                        "title": "角色管理",
                        "icon": "role",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "menu",
                    "component": "system/menu/index",
                    "name": "Menu",
                    "meta": {
                        "title": "菜单管理",
                        "icon": "menu",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "dept",
                    "component": "system/dept/index",
                    "name": "Dept",
                    "meta": {
                        "title": "部门管理",
                        "icon": "tree",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "dict",
                    "component": "system/dict/index",
                    "name": "DictType",
                    "meta": {
                        "title": "字典管理",
                        "icon": "dict",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
            ],

        },
        {
            "path": "/api",
            "component": "Layout",
            "meta": {
                "title": "接口",
                "icon": "api",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "apidoc",
                    "component": "demo/api-doc",
                    "name": "Apidoc",
                    "meta": {
                        "title": "接口文档",
                        "icon": "api",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": False,
                    },
                },
            ],
        },
        {
            "path": "/external-link",
            "component": "Layout",
            "redirect": "noredirect",
            "meta": {
                "title": "外部链接",
                "icon": "link",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "https://juejin.cn/post/7228990409909108793",
                    "meta": {
                        "title": "document",
                        "icon": "document",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
            ],
        },
        {
            "path": "/multi-level",
            "component": "Layout",
            "redirect": "/multi-level/multi-level1",
            "meta": {
                "title": "多级菜单",
                "icon": "multi_level",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "multi-level1",
                    "component": "demo/multi-level/level1",
                    "redirect": "/multi-level/multi-level2",
                    "meta": {
                        "title": "菜单一级",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                    "children": [
                        {
                            "path": "multi-level2",
                            "component": "demo/multi-level/children/level2",
                            "redirect": "/multi-level/multi-level2/multi-level3-1",
                            "meta": {
                                "title": "菜单二级",
                                "icon": "",
                                "hidden": False,
                                "roles": ["ADMIN"],
                                "keepAlive": True,
                            },
                            "children": [
                                {
                                    "path": "multi-level3-1",
                                    "component": "demo/multi-level/children/children/level3-1",
                                    "name": "MultiLevel31",
                                    "meta": {
                                        "title": "菜单三级-1",
                                        "icon": "",
                                        "hidden": False,
                                        "roles": ["ADMIN"],
                                        "keepAlive": True,
                                    },
                                },
                                {
                                    "path": "multi-level3-2",
                                    "component": "demo/multi-level/children/children/level3-2",
                                    "name": "MultiLevel32",
                                    "meta": {
                                        "title": "菜单三级-2",
                                        "icon": "",
                                        "hidden": False,
                                        "roles": ["ADMIN"],
                                        "keepAlive": True,
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        {
            "path": "/component",
            "component": "Layout",
            "meta": {
                "title": "组件封装",
                "icon": "menu",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "wang-editor",
                    "component": "demo/wang-editor",
                    "name": "wang-editor",
                    "meta": {
                        "title": "富文本编辑器",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "upload",
                    "component": "demo/upload",
                    "name": "upload",
                    "meta": {
                        "title": "图片上传",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "icon-selector",
                    "component": "demo/icon-selector",
                    "name": "icon-selector",
                    "meta": {
                        "title": "图标选择器",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "dict-demo",
                    "component": "demo/dict",
                    "name": "DictDemo",
                    "meta": {
                        "title": "字典组件",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "taginput",
                    "component": "demo/taginput",
                    "name": "taginput",
                    "meta": {
                        "title": "标签输入框",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "signature",
                    "component": "demo/signature",
                    "name": "signature",
                    "meta": {
                        "title": "签名",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "table",
                    "component": "demo/table",
                    "name": "Table",
                    "meta": {
                        "title": "表格",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
            ],
        },
        {
            "path": "/table",
            "component": "Layout",
            "meta": {
                "title": "Table",
                "icon": "table",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "dynamic-table",
                    "component": "demo/table/dynamic-table/index",
                    "name": "DynamicTable",
                    "meta": {
                        "title": "动态Table",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "drag-table",
                    "component": "demo/table/drag-table",
                    "name": "DragTable",
                    "meta": {
                        "title": "拖拽Table",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "complex-table",
                    "component": "demo/table/complex-table",
                    "name": "ComplexTable",
                    "meta": {
                        "title": "综合Table",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
            ],
        },
        {
            "path": "/function",
            "component": "Layout",
            "meta": {
                "title": "功能演示",
                "icon": "menu",
                "hidden": False,
                "roles": ["ADMIN"],
                "keepAlive": True,
            },
            "children": [
                {
                    "path": "permission",
                    "component": "demo/permission/page",
                    "name": "Permission",
                    "meta": {
                        "title": "Permission",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "icon-demo",
                    "component": "demo/icons",
                    "name": "Icons",
                    "meta": {
                        "title": "图标",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "websocket",
                    "component": "demo/websocket",
                    "name": "Websocket",
                    "meta": {
                        "title": "Websocket",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
                {
                    "path": "other",
                    "component": "demo/other",
                    "meta": {
                        "title": "敬请期待...",
                        "icon": "",
                        "hidden": False,
                        "roles": ["ADMIN"],
                        "keepAlive": True,
                    },
                },
            ],
        },
    ]
    return {"data": data}
