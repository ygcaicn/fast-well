from typing import Optional, TypeVar, Generic

from pydantic import BaseModel, EmailStr, UUID4, validator


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[str] = None
    password: str

    class Config:
        from_attributes = True


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class JWTTokenData(BaseModel):
    username: str = None


class JWTTokenPayload(BaseModel):
    user_id: int = None


class Msg(BaseModel):
    msg: str


class Captcha(BaseModel):
    captcha_id: str
    captcha_base64: str


class CaptchaVerify(BaseModel):
    captcha_id: str
    value: str


ReponseDataType = TypeVar("ReponseDataType", bound=BaseModel)


class ResponseData(BaseModel, Generic[ReponseDataType]):
    code: int = 0
    data: Optional[ReponseDataType] = None
    msg: Optional[str] = None


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    # captcha_id: str
    # captcha_value: str

    class Config:
        from_attributes = True
