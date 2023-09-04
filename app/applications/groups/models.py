from typing import Optional

import logging

from app.core.base.base_models import BaseCreatedUpdatedAtModel, UUIDDBModel, BaseDBModel

from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.contrib.pydantic import pydantic_model_creator

from app.applications.users.models import User

logger = logging.getLogger(__name__)


class Group(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    parent: fields.ForeignKeyNullableRelation["Group"] = fields.ForeignKeyField(
        "models.Group", related_name="children", null=True)
    children: fields.ReverseRelation["Group"]

    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User", related_name="groups", through="group_user"
    )

    # async def remove_permission(self, permission: str):
    #     if not self.permissions:
    #         self.permissions = []
    #     if permission in self.permissions:
    #         self.permissions.remove(permission)

    # def user_count(self) -> int:
    #     return len(self.users)

    # class PydanticMeta:
    #     computed = ["user_count"]

    def __str__(self):
        return f"<Group:{self.id} {self.name}>"
