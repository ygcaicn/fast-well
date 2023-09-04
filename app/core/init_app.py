import importlib.util
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.core.exceptions import APIException, on_api_exception
from app.core.config import settings
from app.core.log import DEFAULT_LOGGING
from app.core.auth.routes import router as auth_router
from app.applications.users.routes import router as users_router
from app.applications.system.routes import router as system_router
from app.applications.groups.routes import router as groups_router


def configure_logging(log_settings: dict = None):
    log_settings = log_settings or DEFAULT_LOGGING
    logging.config.dictConfig(log_settings)


def init_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )


def _get_tortoise_config() -> dict:
    models = ['aerich.models']
    for app in settings.APPLICATIONS:
        spec = importlib.util.find_spec(f"{app}.models")
        if spec:
            models.append(f"{app}.models")

    config = {
        'connections': settings.DB_CONNECTIONS,
        'apps': {
            'models': {
                'models': models,
                'default_connection': 'default',
            }
        }
    }
    return config


TORTOISE_ORM = _get_tortoise_config()


def register_db(app: FastAPI):
    register_tortoise(app, config=TORTOISE_ORM,
                      generate_schemas=True, add_exception_handlers=True)


def register_exceptions(app: FastAPI):
    app.add_exception_handler(APIException, on_api_exception)


def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix='/api/auth')
    app.include_router(users_router, prefix="/api/users")
    app.include_router(groups_router, prefix="/api/groups")
    app.include_router(system_router, prefix="/api/system")
