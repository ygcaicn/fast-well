import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from typing import Any, List
from pydantic import EmailStr
from pydantic_settings import BaseSettings

_PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir))
_BASE_DIR = os.path.abspath(os.path.join(_PROJECT_ROOT, os.pardir))
sys.path.append(_BASE_DIR)
load_dotenv(os.path.join(_BASE_DIR, '.env'))


class Settings(BaseSettings):
    VERSION: str = '0.1.0'
    APP_TITLE: str = 'Template Application'
    PROJECT_NAME: str = 'Template Application'
    APP_DESCRIPTION: str = 'TG - @AKuzyashin\nhttps://github.com/Kuzyashin'

    SERVER_HOST: str = 'http://localhost:8001'

    DEBUG: bool = True

    APPLICATIONS: List[str] = [
        'app.applications.users',
        'app.applications.groups',
        'app.applications.system',
    ]

    PROJECT_ROOT: str = _PROJECT_ROOT
    BASE_DIR: str = _BASE_DIR
    LOGS_ROOT: str = os.path.join(BASE_DIR, "logs")

    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    JWT_ALGORITHM: str = 'HS25'
    JWT_EXPIRE: int = 60 * 60 * 24 * 7  # 7 day

    REDIS_URL: str = ''

    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://localhost:3000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    CAPTCHA_FONT_PATH: str = os.path.join(
        BASE_DIR, "app/templates/RubikWetPaint-Regular.ttf")

    SUPERUSER: EmailStr = "root@admin.com"
    SUPERUSER_PASSWORD: str = "123456"

    EMAILS_FROM_NAME: str = os.environ.get("EMAILS_FROM_NAME")
    EMAILS_FROM_EMAIL: str = os.environ.get("EMAILS_FROM_EMAIL")
    SMTP_USER: str = os.environ.get("SMTP_USER")
    SMTP_HOST: str = os.environ.get("SMTP_HOST")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT"))
    SMTP_TLS: bool = os.environ.get("SMTP_TLS") in ["True", "true", "1"]
    SMTP_SSL: bool = os.environ.get("SMTP_SSL") in ["True", "true", "1"]
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD")
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAILS_ENABLED: bool = True
    LOGIN_URL: str = SERVER_HOST + '/api/auth/login/access-token'
    EMAIL_TEMPLATES_DIR: str = os.path.join(
        BASE_DIR, "app/templates/emails/build/")

    DB_CONNECTIONS: Any = {
        'default': 'sqlite://./sqlite.db'
    }


settings = Settings()
