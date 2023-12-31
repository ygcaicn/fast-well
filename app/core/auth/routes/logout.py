from datetime import timedelta
from typing import Optional, TypeVar, Generic, Union
from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends, Form
from app.core.auth.deps import get_current_active_superuser, get_current_active_user

from app.core.auth.utils.contrib import send_new_account_email
from app.applications.users.models import User

router = APIRouter()


@router.delete("/")
async def logout(current_user: User = Depends(get_current_active_user)):
    return current_user
