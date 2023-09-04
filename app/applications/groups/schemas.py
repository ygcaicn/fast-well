from .models import Group
from app.applications.users.schemas import BaseUserOut
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
import logging
logger = logging.getLogger(__name__)


class AddUser(BaseModel):
    user_ids: list[int]


class GroupWithUserCount(pydantic_model_creator(Group, name="Group", exclude=('users',))):
    user_count: int


class GroupDetail(pydantic_model_creator(Group, name="Group", exclude=('users',))):
    users: list[BaseUserOut]
