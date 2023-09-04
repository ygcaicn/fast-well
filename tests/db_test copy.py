from tortoise.query_utils import Prefetch
from tortoise import Tortoise, fields, run_async

from app.core.init_app import TORTOISE_ORM
from app.applications.system.models import Menu
from app.applications.system.schemas import MenuType
import logging


async def run():
    await Tortoise.init(config=TORTOISE_ORM)

    await Menu.all().delete()

    try:
        root = Menu(name='root', type=MenuType.CATALOG,
                    path='/', icon='home')
        await root.save()
    except Exception:
        root = await Menu.get(name='root')

    try:
        system = Menu(name='system', type=MenuType.CATALOG,
                      path='/system', icon='setting', parent=root)
        await system.save()
    except Exception:
        system = await Menu.get(name='system')

    try:
        demo = Menu(name='demo', type=MenuType.CATALOG,
                    path='/demo', icon='setting', parent=root)
        await demo.save()
    except Exception:
        ...

    for m in await Menu.all():
        print(m)


if __name__ == "__main__":
    run_async(run())
