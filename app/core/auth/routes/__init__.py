from datetime import timedelta
from typing import Optional, TypeVar, Generic, Union
from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends, Form
from app.core.auth.deps import get_current_active_superuser, get_current_active_user

from app.core.auth.utils.contrib import send_new_account_email
from app.applications.users.models import User

from .login import router as login_router
from .logout import router as logout_router
from .register import router as register_router


router = APIRouter(tags=["auth"])

router.include_router(login_router, prefix="/login")
router.include_router(logout_router, prefix="/logout")
router.include_router(register_router, prefix="/register")

__all__ = ["router"]
