import uuid
from tortoise import models, fields, expressions
from app.core.cache import model_cache
from typing import Any, Optional, Generic, TypeVar


class CacheModelMixin:
    """
    Mixin for caching models
    only works with get and query by id
    """
    CACHE_KEY = "id"

    @classmethod
    async def get(cls, *args, **kwargs):
        if kwargs.get(cls.CACHE_KEY):
            try:
                cache_key = f"CacheModel:{cls.__name__}:{kwargs.get(cls.CACHE_KEY)}"
                cached_data = await model_cache.get(cache_key)
                if cached_data:
                    return cached_data
                else:
                    q: models.Model = await super().get(*args, **kwargs)
                    await model_cache.set(cache_key, q, ttl=600)
                    return q
            except Exception as e:
                ...

        return await super().get(*args, **kwargs)

    @classmethod
    async def delete_cache(cls, key: int = None):
        cache_key = f"CacheModel:{cls.__name__}:{key}"
        await model_cache.delete(cache_key)

    async def save(self, *args, **kwargs):
        await super().save(*args, **kwargs)

        await self.delete_cache(getattr(self, self.CACHE_KEY))
        return self


class BaseDBModel(models.Model):
    id = fields.BigIntField(pk=True, index=True)

    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            d[field] = getattr(self, field)
        for field in self._meta.backward_fk_fields:
            d[field] = await getattr(self, field).all().values()
        return d

    class Meta:
        abstract = True


class UUIDDBModel:
    hashed_id = fields.UUIDField(unique=True, pk=False, default=uuid.uuid4)


class BaseCreatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)


class BaseCreatedUpdatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
