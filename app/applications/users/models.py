from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.applications.users.schemas import BaseUserCreate
from app.core.base.base_models import BaseCreatedUpdatedAtModel, UUIDDBModel, BaseDBModel
from app.core.auth.utils import password
from app.core.cache import model_cache


class User(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    username = fields.CharField(max_length=20, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    nickname = fields.CharField(max_length=50, null=True)
    password_hash = fields.CharField(max_length=128, null=True)
    last_login = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    is_confirmed = fields.BooleanField(default=False)
    avatar = fields.CharField(max_length=512, null=True)

    groups: fields.ReverseRelation["Group"]
    roles: fields.ReverseRelation["Role"]

    def full_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    @property
    def permissions(self) -> set[str]:
        _permissions = []
        if self.groups:
            _permissions = [p for g in self.groups for p in g.permissions]

        return set(_permissions)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(email=email)
            user = await query
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        try:
            query = cls.get(username=username)
            user = await query
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def create(cls, user: BaseUserCreate) -> "User":
        user_dict = user.model_dump(exclude_unset=True)
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash)
        await model.save()
        return model

    @classmethod
    async def delete_cache(cls, user_id: str) -> None:
        await model_cache.delete(f"user:{user_id}")

    class Meta:
        table = 'users'

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ("password_hash",)

    def __str__(self):
        return f"<User:{self.id} {self.username} {self.email}>"
