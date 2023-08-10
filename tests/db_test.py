from tortoise.query_utils import Prefetch
from tortoise import Tortoise, fields, run_async

from app.core.init_app import TORTOISE_ORM
from app.applications.users.models import User, Group

from app.applications.users.schemas import BaseProperties

import logging

# logging.basicConfig(level=logging.DEBUG)
from aiocache import caches
from aiocache.serializers import PickleSerializer


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    cache_config = {
        "default": {
            "cache": "aiocache.RedisCache",
            "endpoint": "localhost",
            "port": 6379,
            "serializer": {
                "class": PickleSerializer
            }
        }
    }
    caches.set_config(cache_config)

    cache = caches.get("default")
    cache_key = "users"
    # 尝试从缓存中获取数据
    cached_data = await cache.get(cache_key)
    if cached_data:
        print("cached", cached_data)
        return cached_data

    # 如果缓存中没有数据，则从数据库中获取数据
    users = await User.all().values()

    # 将数据存入缓存
    await cache.set(cache_key, users, ttl=3600)  # 设置缓存过期时间为1小时

    # a = await Group.filter(name='admin').count()

    # if a == 0:
    #     g = await Group.create(name='admin')
    # else:
    #     g = await Group.get(name='admin').prefetch_related('users')

    # print(await g.fetch_related("users"))
    # await g.add_permission("test")
    # await g.save()
    # print(await g.to_dict())

    # admin_group = await Group.get(name='admin').prefetch_related('users').values('permissions', 'users__id')
    # print(admin_group)

    # user = await User.get(username='root@admin.com').prefetch_related('groups')
    # print(user.permissions)
    # print([g for g in user.groups])

    # print(permissions, user_ids)
    # users = await User.all()
    # for user in users:
    #     print(user)
    #     print("Groups:", await user.groups.all())
    #     if user.is_superuser:
    #         await user.groups.add(g)
    #         await user.save()


if __name__ == "__main__":
    run_async(run())
