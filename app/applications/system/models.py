
from .schemas import MenuType, MenuOut
from app.core.base.base_models import BaseCreatedUpdatedAtModel, UUIDDBModel, BaseDBModel, CacheModelMixin
from app.applications.users.schemas import BaseUserCreate
from tortoise.exceptions import DoesNotExist
from tortoise import fields
from typing import Optional
import logging

from app.applications.users.models import User

logger = logging.getLogger(__name__)


class Menu(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    name = fields.CharField(max_length=128, unique=True)
    parent: fields.ForeignKeyNullableRelation["Menu"] = fields.ForeignKeyField(
        "models.Menu", related_name="children", null=True)
    children: fields.ReverseRelation["Menu"]

    type = fields.CharEnumField(MenuType, default=MenuType.MENU)

    path = fields.CharField(max_length=128, null=True)
    icon = fields.CharField(max_length=128, null=True)
    redirect = fields.CharField(max_length=128, null=True)

    component = fields.CharField(max_length=128, null=True)

    # for button permission
    permission_key = fields.CharField(max_length=128, null=True)

    external_link = fields.CharField(max_length=128, null=True)

    active = fields.BooleanField(default=True)
    sort = fields.IntField(null=True)

    is_deleted = fields.BooleanField(default=False)

    async def full_hierarchy__fetch_related(self, level=0):
        await self.fetch_related("children")
        if self.children:
            for child in self.children:
                await child.full_hierarchy__fetch_related(level + 1)
        return self

    @classmethod
    async def full_hierarchy_menu(cls, parent=None, query: Optional[str] = None) -> list[MenuOut]:
        result = []
        query_set = cls.filter(parent=parent, is_deleted=False)
        if query:
            query_set = query_set.filter(name__icontains=query)
        root_menus = await query_set.order_by("sort", "id").all()

        for root in root_menus:
            d = {}
            print(root._meta.db_fields)
            for field in root._meta.db_fields:
                d[field] = getattr(root, field)
            d["parent_id"] = parent.id if parent else None
            d["children"] = await cls.full_hierarchy_menu(root, query)
            result.append(MenuOut(**d))

        return result

    @classmethod
    async def full_hierarchy_catalog(cls, parent=None):
        result = []
        root_menus = await cls.filter(parent=parent, type__in=[MenuType.CATALOG, MenuType.MENU], active=True).order_by("sort", "id").all()
        for root in root_menus:
            result.append({
                "value": root.id,
                "label": root.name,
                "children": await cls.full_hierarchy_catalog(root)
            })

        return result

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"{self.name}"


class Role(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    name = fields.CharField(max_length=128, unique=True)
    key = fields.CharField(max_length=128, unique=True)
    description = fields.TextField(null=True)
    active = fields.BooleanField(default=True)
    sort = fields.IntField(default=0, null=False)
    permissions: fields.ManyToManyRelation[Menu] = fields.ManyToManyField(
        "models.Menu", related_name="roles", through="role_menu"
    )
    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User", related_name="roles", through="role_user"
    )

    def __str__(self):
        return f"<Role:{self.id} {self.name}>"
