from fastapi import APIRouter, Depends, HTTPException

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=['system'])


@router.get("/")
async def hello():
    return {"message": "Hello World"}
