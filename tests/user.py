#! /usr/bin/env python3

import logging
from app.core.config import settings
from app.applications.users.schemas import BaseUserCreate
from app.applications.users.models import User
from app.core.init_app import TORTOISE_ORM

from tortoise import Tortoise, run_async

logging.basicConfig(level=logging.INFO)


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(config=TORTOISE_ORM)
    # Generate the schema
    await Tortoise.generate_schemas()


async def create_super_user():
    if settings.SUPERUSER:
        user = await User.get_by_email(email=settings.SUPERUSER)
        if not user:
            db_user = BaseUserCreate(
                **{
                    'username': 'root',
                    'email': settings.SUPERUSER,
                    'password': settings.SUPERUSER_PASSWORD,
                }
            )
            created_user = await User.create(db_user)
            created_user.is_superuser = True
            await created_user.save()

            user = create_super_user
            logging.info(f'Created superuser: {created_user}')
        else:
            logging.info(f'Superuser already exists: {user}')

        print(user.password_hash)


async def main():
    await init()
    await create_super_user()


if __name__ == '__main__':
    run_async(main())
