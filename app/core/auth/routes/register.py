import inspect
from typing import Any, Type, TypeVar, Union, Optional, List, Dict, Callable, Awaitable, Annotated
from pydantic import BaseModel, EmailStr, UUID4, validator, Field

from datetime import timedelta
from typing import Optional, TypeVar, Generic, Union
from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends, Form
from app.core.auth.deps import get_current_active_superuser, get_current_active_user

from app.core.auth.utils.contrib import send_new_account_email, generate_account_confirm_token, send_account_confirm_email, verify_account_confirm_token
from app.applications.users.models import User
from app.applications.users.schemas import BaseUserCreate
from app.core.config import settings
from app.core.auth.utils.captcha import get_captcha, verify_captcha
from app.core.auth.schemas import RegisterUser
router = APIRouter()


class RegisterUserForm:
    def __init__(
        self,
        *,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        password_confirm: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        captcha_id: Annotated[str, Form()],
        captcha_value: Annotated[str, Form()],
    ):
        self.username = username
        self.password = password
        self.password_confirm = password_confirm
        self.email = email
        self.captcha_id = captcha_id
        self.captcha_value = captcha_value


@router.post("/")
async def register(background_tasks: BackgroundTasks,
                   form_data: Annotated[RegisterUserForm, Depends()]
                   ):
    try:
        _user = RegisterUser.model_validate(form_data)
        _user = BaseUserCreate.model_validate(_user.model_dump())
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Incorrect email or password") from e

    captcha_verifyd = await verify_captcha(form_data.captcha_value, form_data.captcha_id)

    created_user = await User.create(_user)

    if settings.EMAILS_ENABLED:
        token = generate_account_confirm_token(
            created_user.id, created_user.email)
        background_tasks.add_task(
            send_account_confirm_email, email_to=created_user.email, username=created_user.username, token=token
        )

    return {"captchat": captcha_verifyd, "user": created_user}


@router.get("/account-confirm")
async def account_confirm(token: str):
    """
    Account confirm
    """
    verifyd = verify_account_confirm_token(token)
    if not verifyd:
        raise HTTPException(
            status_code=403, detail="Invalid link")
    else:
        user = await User.get(id=verifyd[0], email=verifyd[1])
        user.is_confirmed = True
        await user.save()
    return {"msg": user}


@router.get("/rquest-account-confirm")
async def rquest_account_confirm(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_active_user),):
    """
    Request account confirm
    """
    if current_user.is_confirmed:
        raise HTTPException(
            status_code=400, detail="User already confirmed")
    else:
        token = generate_account_confirm_token(
            current_user.id, current_user.email)
        background_tasks.add_task(
            send_account_confirm_email, email_to=current_user.email, username=current_user.username, token=token
        )
        return {"token": token}
