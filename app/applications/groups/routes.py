from tortoise.functions import Count
from .schemas import AddUser, GroupWithUserCount, GroupDetail
from .models import Group
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, TypeVar

from tortoise import models, fields, expressions
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.applications.users.models import User

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=['groups'])


@router.get("/", response_model=list[GroupWithUserCount])
async def groups(keywords: Optional[str] = None,
                 page: Optional[int] = Query(title="page", ge=1, default=1),
                 page_size: Optional[int] = Query(title="page_size", le=20, default=10)):
    if keywords:
        query = Group.filter(name__icontains=keywords)
    else:
        query = Group.all()

    query = query.offset((page-1) * page_size).limit(page_size)
    query = query.annotate(user_count=Count('users')).all()
    return await GroupWithUserCount.from_queryset(query)


@router.post("/")
async def create_group(name: str, description: Optional[str] = None):
    g = await Group.create(name=name, description=description)

    return g


@router.get("/{group_id}")
async def group(group_id: int):
    g = await Group.get_or_none(id=group_id).prefetch_related('users')
    if g is None:
        return HTTPException(status_code=404, detail="Item not found")

    # await g.users
    # # PydanticGroup = pydantic_model_creator(Group)
    # print(g.users)

    return await GroupDetail.from_tortoise_orm(g)


@router.put("/{group_id}/user")
async def add_user_to_group(group_id: int, schema: AddUser):
    g = await Group.get_or_none(id=group_id).prefetch_related("users")
    if g is None:
        return HTTPException(status_code=404, detail="Item not found")

    print("-----------")
    # print(await g.users)
    users = await User.filter(id__in=schema.user_ids)
    if len(users) > 0:
        await g.users.add(*users)
        print(g)
    return users
