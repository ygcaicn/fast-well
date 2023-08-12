from aiocache.serializers import PickleSerializer
from aiocache import caches
import redis.asyncio as redis


def get_cache():
    return redis.from_url("redis://localhost",
                          encoding="utf-8", decode_responses=True)


cache = get_cache()

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


model_cache = caches.get("default")
