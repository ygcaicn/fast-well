from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from app.core.exceptions import SettingNotFound
from app.core.init_app import (configure_logging, init_middlewares, register_db,
                               register_exceptions, register_routers)
from app.core.cache import get_cache

try:
    from app.core.config import settings
except ImportError as exc:
    raise SettingNotFound('Can not import settings.') from exc


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION
)

configure_logging()
init_middlewares(app)
register_db(app)
register_exceptions(app)
register_routers(app)


@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(get_cache())
