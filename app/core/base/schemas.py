from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

ReponseDataType = TypeVar("ReponseDataType", bound=BaseModel)


class ResponseData(BaseModel, Generic[ReponseDataType]):
    code: int = 0
    data: Optional[ReponseDataType] = None
    msg: Optional[str] = None
