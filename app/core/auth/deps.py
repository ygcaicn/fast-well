from typing import Union, Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.applications.users.models import User
from app.core.auth.schemas import JWTTokenPayload
from app.core.auth.utils.captcha import verify_captcha
from app.core.auth.utils.jwt import ALGORITHM
from app.core.cache import model_cache
from app.core.config import settings
from app.core.auth.schemas import CredentialsSchema

from app.core.auth.utils.contrib import (generate_password_reset_token,
                                         send_reset_password_email,
                                         verify_password_reset_token,
                                         authenticate)

from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends, Security, Form
from jose import JWTError, jwt
from starlette.status import HTTP_403_FORBIDDEN

from app.applications.users.utils import update_last_login
from typing import List, Optional
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login/access-token")


async def get_access_token_data(token: str = Security(reusable_oauth2)) -> Optional[JWTTokenPayload]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        token_data = JWTTokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    return token_data


async def get_current_user(token: str = Security(reusable_oauth2)) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        token_data = JWTTokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    try:
        cached_user = await model_cache.get(f"user:{token_data.user_id}")
    except Exception:
        cached_user = None

    if cached_user:
        user = cached_user
    else:
        try:
            user = await User.get(id=token_data.user_id).prefetch_related('groups')
        except Exception:
            user = None
        if user:
            await model_cache.set(f"user:{token_data.user_id}", user, 600)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(current_user: User = Security(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(current_user: User = Security(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def permissions_required(permissions: Optional[List[str]] = None):
    async def user_has_permission(user: User = Security(get_current_user)) -> User:
        if user.is_superuser:
            return user
        if not permissions:
            return user

        for need_permission in permissions:
            if need_permission not in user.permissions:
                raise HTTPException(status_code=403, detail="没有权限")

        return user

    return user_has_permission


class CaptchaForm:
    def __init__(self, captcha_id: str = Form(...), captcha_value: str = Form(...)):
        self.captcha_id = captcha_id
        self.captcha_value = captcha_value


async def captcha_verify_required(form_data: CaptchaForm = Depends()):
    verified = await verify_captcha(form_data.captcha_value, form_data.captcha_id)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid captcha")
    return verified


async def authentication_required(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = await authenticate(CredentialsSchema.model_validate(form_data))
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password") from exc

    if user:
        await update_last_login(user.id)
    elif not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
