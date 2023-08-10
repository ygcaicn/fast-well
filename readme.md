pip install fastapi
pip install "uvicorn[standard]"
pip install 'python-jose[cryptography]'
pip install 'passlib[bcrypt]'

pip install 'pydantic[email]'
pip install pydantic-settings
pip install python-multipart
pip install 'celery[redis]'

pip install tortoise-orm
pip install aerich

pip install emails
pip install jinja2
pip install pyjwt
pip install 'python-jose[cryptography]'

pip install fastapi-limiter

aerich init -t  app.core.init_app.TORTOISE_ORM
aerich migrate
aerich upgrade

pip install "aiocache[redis,memcached]"

uvicorn app.main:app --reload --port 8001 --reload-dir app/




pip install -U prisma

export PYTHONPATH="./"



celery -A app.core.celery worker -l INFO
