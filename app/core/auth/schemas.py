from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator, ValidationError, validate_email


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr] = None
    password: str

    class Config:
        from_attributes = True

    # @model_validator(mode='after')
    # def check_passwords_match(self) -> 'CredentialsSchema':
    #     try:
    #         _, email = validate_email(self.username)
    #         self.email = email
    #     except Exception:
    #         ...
    #     return self


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


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'RegisterUser':
        pw1 = self.password
        pw2 = self.password_confirm
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
