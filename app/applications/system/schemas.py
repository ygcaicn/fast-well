from enum import Enum
from typing import Optional, TypeVar, List
from pydantic import BaseModel, EmailStr, UUID4, validator

import logging
logger = logging.getLogger(__name__)


class RouteMeta(BaseModel):
    title: str
    icon: Optional[str] = None
    hidden: bool = False
    roles: Optional[list] = ['ADMIN']
    keepAlive: bool = True


class Route(BaseModel):
    path: str
    meta: RouteMeta
    component: Optional[str] = None
    redirect: Optional[str] = None
    name: Optional[str] = None
    children: Optional[list['Route']] = []


class MenuType(str, Enum):
    CATALOG = "CATALOG"
    MENU = "MENU"
    BUTTON = "BUTTON"
    EXTERNAL_LINK = "EXTERNAL_LINK"


class Catalog(BaseModel):
    label: str
    value: int  # pk id
    children: Optional[list['Catalog']] = []


class MenuOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: Optional[list['MenuOut']] = []
    type: MenuType = MenuType.MENU
    path: Optional[str] = None
    icon: Optional[str] = None
    redirect: Optional[str] = None
    component: Optional[str] = None
    permission_key: Optional[str] = None
    external_link: Optional[str] = None
    active: bool = True
    sort: Optional[int] = None

    class Config:
        from_attributes = True


class MenuIn(BaseModel):
    name: str
    parent_id: Optional[int] = None
    type: MenuType = MenuType.MENU
    path: Optional[str] = None
    icon: Optional[str] = None
    redirect: Optional[str] = None
    component: Optional[str] = None
    permission_key: Optional[str] = None
    external_link: Optional[str] = None
    active: bool = True
    sort: Optional[int] = None

    class Config:
        from_attributes = True


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    type: Optional[MenuType] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    redirect: Optional[str] = None
    component: Optional[str] = None
    permission_key: Optional[str] = None
    external_link: Optional[str] = None
    active: Optional[bool] = None
    sort: Optional[int] = None

    class Config:
        from_attributes = True


class PageQuery(BaseModel):
    page: int = 1
    page_size: int = 10


class RoleOut(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str] = None
    active: bool = True

    class Config:
        from_attributes = True


class RoleOutList(BaseModel):
    total: int
    items: List[RoleOut]

    class Config:
        from_attributes = True


class RoleIn(BaseModel):
    name: str
    key: str
    description: Optional[str] = None
    active: bool = True

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

    class Config:
        from_attributes = True
