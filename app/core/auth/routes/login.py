from datetime import timedelta
from typing import Union, Annotated

from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter

from app.applications.users.models import User
from app.applications.users.utils import update_last_login
from app.core.auth.deps import captcha_verify_required
from app.core.auth.schemas import (JWTToken, Msg, Captcha, CaptchaVerify)
from app.core.auth.utils.contrib import (generate_password_reset_token,
                                         send_reset_password_email,
                                         verify_password_reset_token,
                                         authenticate)
from app.core.auth.utils.jwt import create_access_token
from app.core.auth.utils.password import get_password_hash
from app.core.auth.utils.captcha import get_captcha, verify_captcha
from app.core.base.schemas import ResponseData
from app.core.config import settings
from app.core.auth.deps import authentication_required

router = APIRouter()


@router.post("/", response_model=ResponseData[JWTToken])
async def login(user: User = Depends(authentication_required), verified: bool = Depends(captcha_verify_required)):
    assert verified, "Invalid captcha"
    access_token_expires = timedelta(seconds=settings.JWT_EXPIRE)
    return {
        "code": 0,
        "data": {
            "access_token": create_access_token(data={"user_id": user.id},
                                                expires_delta=access_token_expires),
            "token_type": "bearer",
        },
        "msg": "Login successful"
    }


@router.post("/access-token", response_model=JWTToken)
async def login_access_token(user=Depends(authentication_required)):
    access_token_expires = timedelta(seconds=settings.JWT_EXPIRE)
    return {
        "access_token": create_access_token(data={"user_id": user.id},
                                            expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/password-recovery/{email}", response_model=Msg)
async def recover_password(email: str, background_tasks: BackgroundTasks):
    """
    Password Recovery
    """
    user = await User.get_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    background_tasks.add_task(
        send_reset_password_email, email_to=user.email, email=email, token=password_reset_token)
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=Msg)
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await User.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    await user.save()
    return {"msg": "Password updated successfully"}


@router.get("/captcha", response_model=ResponseData[Captcha], dependencies=[Depends(RateLimiter(times=50, seconds=300))])
async def captcha():
    """
    Get captcha
    """
    get_captcha_result = await get_captcha()

    return {"code": 0,
            "msg": "Captcha obtained successfully", "data":
                {
                    "captcha_id": get_captcha_result[1],
                    "captcha_base64": get_captcha_result[0]
                },
            }


@router.post("/captcha", response_model=Union[ResponseData[int], ResponseData[Captcha]], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def captcha_verify(verify: CaptchaVerify):
    verifyd = await verify_captcha(verify.captcha_id, verify.value)
    if verifyd:
        return {
            "code": "0",
            "msg": "Captcha verification successful",
            "data": 1
        }
    else:
        get_captcha_result = await get_captcha()
        return {
            "code": "1",
            "msg": "Captcha verification failed",
            "data": {"captcha_id": get_captcha_result[1], "captcha_base64": get_captcha_result[0]}
        }
