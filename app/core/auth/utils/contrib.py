import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import emails
from jose import JWTError, jwt
from emails.template import JinjaTemplate

from app.applications.users.models import User
from app.core.auth.utils import password
from app.core.config import settings
from app.core.auth.schemas import CredentialsSchema

PASSWORD_RESET_JWT_SUBJECT = "passwordreset"


def send_email(email_to: str, subject_template="", html_template="", environment={}):
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")
    return response


def send_reset_password_email(email_to: str, username: str, token: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email_to}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "password_reset.html") as f:
        template_str = f.read()
    if hasattr(token, "decode"):
        use_token = token.decode()
    else:
        use_token = token
    server_host = settings.SERVER_HOST
    link = f"{server_host}/auth/reset-password?token={use_token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.LOGIN_URL
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def send_account_confirm_email(email_to: str, username: str, token: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Confirm account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "confirm_account.html") as f:
        template_str = f.read()
    if hasattr(token, "decode"):
        user_token = token.decode()
    else:
        user_token = token
    server_host = settings.SERVER_HOST
    link = f"{server_host}/api/auth/register/account-confirm?token={user_token}"
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def generate_password_reset_token(email):
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    encoded_jwt = jwt.encode(
        {"exp": expires, "nbf": now, "sub": PASSWORD_RESET_JWT_SUBJECT, "email": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token) -> Optional[str]:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == PASSWORD_RESET_JWT_SUBJECT
        return decoded_token["email"]
    except JWTError:
        return None


def generate_account_confirm_token(user_id, email):
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    encoded_jwt = jwt.encode(
        {"exp": expires, "nbf": now, "sub": 'account_confirm',
            "email": email, "user_id": user_id},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_account_confirm_token(token) -> Optional[tuple]:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == 'account_confirm'
        return decoded_token["user_id"], decoded_token["email"]
    except JWTError:
        return None


async def authenticate(credentials: CredentialsSchema) -> Optional[User]:
    print(credentials)
    user = None
    if credentials.email:
        user = await User.get_by_email(credentials.email)

    if user is None and credentials.username:
        user = await User.get_by_username(credentials.username)

    if user is None and credentials.username:
        user = await User.get_by_email(credentials.username)

    if user is None:
        return None

    verified, updated_password_hash = password.verify_and_update_password(
        credentials.password, user.password_hash
    )

    if not verified:
        return None
        # Update password hash to a more robust one if needed
    if updated_password_hash is not None:
        user.password_hash = updated_password_hash
        await user.save()
    return user
