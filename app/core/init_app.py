import importlib.util
from app.applications.users.models import User
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.core.exceptions import APIException, on_api_exception
from app.core.config import settings
from app.core.log import DEFAULT_LOGGING
from app.core.auth.routes import router as auth_router
from app.applications.users.routes import router as users_router
from app.applications.users.schemas import BaseUserOut, BaseUserCreate, BaseUserUpdate
from app.core.auth.utils.password import get_password_hash


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


async def create_super_user():
    if settings.SUPERUSER:
        user = await User.get_by_email(email=settings.SUPERUSER)
        if not user:
            db_user = BaseUserCreate(
                **{
                    'username': settings.SUPERUSER,
                    'email': settings.SUPERUSER,
                    'password': settings.SUPERUSER_PASSWORD,
                }

            )
            created_user = await User.create(db_user)
            logging.info(created_user)
            logging.info(f'Created superuser: {settings.SUPERUSER}')
        elif not user.is_superuser:
            user.is_superuser = True
            await user.save()


def register_exceptions(app: FastAPI):
    app.add_exception_handler(APIException, on_api_exception)


def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix='/api/auth')
    app.include_router(users_router, prefix="/users")
