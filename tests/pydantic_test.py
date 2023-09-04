from pydantic import BaseModel, EmailStr, model_validator, ValidationError, validate_email
from typing import Any, List, Optional
from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator,
)


from pydantic.functional_validators import AfterValidator

from pydantic import functional_validators, model_validator


class DemoModel(BaseModel):
    number: Annotated[int,
                      functional_validators.AfterValidator(lambda x: x > 0)]

    @field_validator("number")
    @classmethod
    def check_number(cls, v, values, **kwargs):
        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        return 1


# a = DemoModel(number=1)
# print(type(a))
# print(type(a.number))
# print(DemoModel(number=1))


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr | str] = None
    password: str

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'CredentialsSchema':
        try:
            _, e = validate_email(self.username)
            self.email = e
        except ValidationError as e:
            print(e)
        return self


print(CredentialsSchema(
    **{"username": " abc@@o.m", "password": "x"}))


# email = EmailStr('test@example.com')
# email.validate()  # 验证电子邮件地址
# print(email)
